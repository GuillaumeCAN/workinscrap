# ==============================================================================
#  This file is part of a private project and is intended for educational use only.
#  Unauthorized copying, distribution, or modification of this file, in whole or
#  in part, without explicit written permission from the author is strictly prohibited.
#
#  DISCLAIMER:
#  This program is not intended to be used for cheating, academic dishonesty,
#  or any other unethical activities. It is provided solely for learning and
#  research purposes.
#
#  © Guillaume CANCALON – All rights reserved.
# ==============================================================================

from rich.console import Console

from app.get_user import get_course_list
import app.ai_request as ai_request
import threading
import time

from app import log, idle
from app.get_user import is_api_key_valid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

console = Console()
scraping_status = False

def is_scraping(driver=None, connected=False):
    return scraping_status

def get_status_text():
    if scraping_status:
        return [("class:status_green", "  🟩 Now scraping..."),]
    else:
        return [("class:status_red", "  🔴 Scraping stopped.")]

def warn_status_text():
    if idle.is_idling():
        return [("class:warn", "  ⚠️  [WARN] Idle daemon is currently running.\n"),
                ("class:warn", "     It may cause problems during the scrap ! Turn off idle to avoid any troubles")]
    else:
        return []

def api_key_status():
    if not is_api_key_valid():
        return [
            ("class:warn", "  🔑 API Key invalid or not found !\n"),
            ("class:warn", "     Please check your Gemini API key in config.py."),
        ]
    else:
        return [
            ("class:status_green", "  🔑 Gemini API Key is valid — you're ready to scrap !")
        ]

def get_courses(driver=None, connected=False):
    courses = get_course_list(driver, connected)
    return courses

def toggle_scraping(driver=None, selected_module=None):
    global scraping_status
    if not scraping_status:
        scraping_status = True
        scraping_thread = threading.Thread(target=start_scraping, args=(driver, selected_module), daemon=True)
        scraping_thread.start()
    else:
        scraping_status = False

def start_scraping(driver, module):
    global scraping_status
    log.info(f"Scraping thread started for : {module}")

    try:
        # wait until the module cards are present
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "progress-card"))
        )
        log.debug("Module cards loaded successfully.")

        # retrieve all module cards
        module_cards = driver.find_elements(By.CLASS_NAME, "progress-card")

        # find the one that corresponds to the desired module
        target_card = None
        for card in module_cards:
            try:
                title_elem = card.find_element(By.TAG_NAME, "h3")
                title = title_elem.text.strip()
                if module.lower() in title.lower():
                    target_card = card
                    break
            except Exception:
                continue

        if not target_card:
            log.error(f"Module '{module}' not found")
            scraping_status = False
            return

        log.scrap(f"Module : {module} found. Entering module...")
        try:
            access_link = None
            try:
                access_link = target_card.find_element(
                    By.XPATH, ".//div[contains(@class, 'card-action')]//a"
                )
            except Exception:
                pass

            if not access_link:
                access_link = target_card.find_element(
                    By.XPATH, ".//div[contains(@class, 'card-action')]//button"
                )

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", access_link)
            time.sleep(0.5)

            try:
                back_btn = driver.find_element(By.XPATH, "//span[contains(@class, 'back-btn__text')]")
                if back_btn.is_displayed():
                    log.debug("Back button detected — attempting to hide it temporarily.")
                    driver.execute_script("arguments[0].style.display = 'none';", back_btn)
            except Exception:
                pass

            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(access_link))
                driver.execute_script("arguments[0].click();", access_link)
                log.scrap("Entered module successfully.")

            except Exception as e:
                log.warn(f"Error : {e}")

        except Exception as e:
            log.error(f"Error while trying to access module : {e}")
            scraping_status = False
            return

        #SCRAP LOGIC
        complete_module_exercises(driver, module)

    except Exception as e:
        log.error(f"[SCRAP] Error inside start_scraping: {e}")

    finally:
        log.info("Scraping thread stopped.")


def solve_qcm(driver):
    try:
        question_index = 1
        log.debug("🔁 Start of the MCQ loop...")

        while True:
            # trying end_btn
            try:
                end_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[.//span[contains(normalize-space(.), 'Terminer le QCM')]]")
                    )
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", end_btn)
                time.sleep(0.4)

                # JS safety
                driver.execute_script("arguments[0].click();", end_btn)
                log.scrap("MQC ending. Fetching result...")
                break

            except Exception as e:
                pass

            # Wait for a question to be displayed
            time.sleep(1)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'question')]//p | //h3"))
            )
            question_elem = driver.find_element(By.XPATH, "//div[contains(@class,'question')]//p | //h3")
            question_text = question_elem.text.strip()

            # Retrieve the choices
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "card__answers__item"))
            )
            choice_elements = driver.find_elements(By.CLASS_NAME, "card__answers__item")
            choices = []
            for choice_elem in choice_elements:
                try:
                    text_elem = choice_elem.find_element(By.CLASS_NAME, "text")
                    choice_text = text_elem.text.strip()
                except Exception:
                    choice_text = choice_elem.text.strip()
                if choice_text:
                    choices.append(choice_text)

            log.scrap(f"🧩 Question {question_index} detected : {question_text}")
            for c in choices:
                log.scrap(f"   - {c}")

            # Response via Gemini
            answer = ai_request.ask_gemini(question_text, choices)
            log.scrap(f"🤖 Gemini offers: {answer}")

            # Select the correct answer
            selected = None
            for choice_elem in choice_elements:
                if answer.lower().strip() in choice_elem.text.lower().strip():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", choice_elem)
                    choice_elem.click()
                    selected = choice_elem.text.strip()
                    break

            if not selected:
                log.warn(f"⚠️ Answer '{answer}' not found among the options.")
                break

            log.scrap(f"✅ Selected answer : {selected}")

            # Click on 'Validate'
            try:
                validate_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Valider')]"))
                )
                validate_btn.click()
                log.debug("Clicked 'Valider' button.")
            except Exception:
                log.warn("⚠️ Unable to find the 'Validate' button")
                break

            # Wait for the question to be updated (text changed or removed)
            try:
                WebDriverWait(driver, 10).until_not(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, "//div[contains(@class,'question')]//p | //h3"), question_text
                    )
                )
                log.debug("New question detected.")
                question_index += 1
                continue

            except Exception:
                log.error("No question detected and no finish button detected either... exiting scrap")
                break


        #RESULT
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "score__value"))
            )
            score = driver.find_element(By.CLASS_NAME, "score__value").text.strip()
            log.info(f"Score : {score}")
        except Exception as e:
            log.error(f"Unable to fetch score: {e}")


        #QUIT RESULT
        try:
            quit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Quitter le QCM ')]")
                )
            )
            driver.execute_script("arguments[0].click();", quit_btn)
        except Exception as e:
            log.error(f"Unable to quit result: {e}")

        #QUIT MODULE
        try:
            return_to_module = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Retour à la liste des cours')]")
                )
            )
            driver.execute_script("arguments[0].click();", return_to_module)

        except Exception as e:
            log.error(f"Unable to fetch quit button: {e}")

    except Exception as e:
        log.error(f"[QCM] Error inside solve_qcm : {e}")


def complete_module_exercises(driver, module_name):
    log.info(f"Exercise processing begins for the module: {module_name}")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "exercise-card"))
        )
        all_exercise_cards = driver.find_elements(By.CLASS_NAME, "exercise-card")

        # filter non-done exercise
        exercise_cards = [
            card for card in all_exercise_cards
            if "is-done" not in card.get_attribute("class")
        ]

        log.scrap(f"{len(exercise_cards)} incomplete exercises found in module '{module_name}' "
                  f"(out of {len(all_exercise_cards)} total).")

        for i in range(len(exercise_cards)):
            try:
                # refresh card-list
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "exercise-card"))
                )
                all_exercise_cards = driver.find_elements(By.CLASS_NAME, "exercise-card")

                # filter is-done
                exercise_cards = [
                    c for c in all_exercise_cards
                    if "is-done" not in c.get_attribute("class")
                ]

                if i >= len(exercise_cards):
                    log.scrap("🚀 All exercises have been updated or completed!")
                    toggle_scraping(driver)
                    break

                card = exercise_cards[i]
                title_elem = card.find_element(By.TAG_NAME, "h3")
                title = title_elem.text.strip()
                log.scrap(f"→ Exercise {i + 1}: {title}")

                # access to exercise
                access_link = card.find_element(By.XPATH, ".//a[contains(@class,'exercise-card-link')]")
                driver.execute_script("arguments[0].scrollIntoView(true);", access_link)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", access_link)
                log.scrap(f"Access to exercise '{title}' successfully.")

                # access to mqc
                try:
                    log.debug("Waiting for QCM card to appear...")
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, "mcq-cta-card"))
                    )
                    time.sleep(1)

                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        driver.switch_to.frame(iframes[0])
                        log.debug("Switched into iframe containing QCM button.")

                    qcm_button = None
                    possible_selectors = [
                        "//button[.//span[contains(translate(text(), 'ACCEDER AU QCM', 'acceder au qcm'),'acceder au qcm')]]",
                        "//span[contains(text(), 'Accéder au QCM')]/ancestor::button",
                        "//div[@id='mcq-cta-card']//button",
                    ]

                    for selector in possible_selectors:
                        try:
                            qcm_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                            if qcm_button:
                                break
                        except Exception:
                            continue

                    if not qcm_button:
                        raise Exception("The 'Access the MCQ' button cannot be found even after several attempts.")

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", qcm_button)
                    time.sleep(0.8)
                    driver.execute_script("arguments[0].click();", qcm_button)
                    log.scrap(f"Clicked 'Access the quiz' button for: {title}")

                    driver.switch_to.default_content()

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Valider')] | //form"))
                    )

                    begin_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "/html/body/div/div/div/main/section/div/div/div[1]/div[2]/button")
                        )
                    )
                    driver.execute_script("arguments[0].click();", begin_btn)
                    log.scrap(f"Multiple-choice questions loaded for: {title}")

                    # mqc solver
                    solve_qcm(driver)

                except Exception as e:
                    log.warn(f"Unable to access the multiple-choice quiz for {title}: {e}")
                    driver.switch_to.default_content()
                    continue

            except Exception as e:
                log.warn(f"Error processing exercise {i + 1}: {e}")
                driver.switch_to.default_content()
                continue

    except Exception as e:
        log.error(f"Error while scraping exercises : {e}")
