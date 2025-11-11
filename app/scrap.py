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
from selenium.webdriver.common.devtools.v137.fetch import fail_request

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
        driver.back()

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
                access_link.click()
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
            # Wait for a question to be displayed
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
                log.scrap("✅ End of MCQ detected (no more questions).")
                break

        # Final step: click the "Finish" button
        try:
            log.debug("Looking for the 'Finish' button...")

            # Try several possible selectors
            possible_end_btns = [
                "//button[.//span[contains(translate(text(),'TERMINER','terminer'),'terminer')]]",
                "//button[contains(translate(text(),'TERMINER','terminer'),'terminer')]",
                "//span[contains(text(),'Terminer')]/ancestor::button",
            ]

            end_btn = None
            for selector in possible_end_btns:
                try:
                    end_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if end_btn:
                        break
                except Exception:
                    continue

            if not end_btn:
                raise Exception("The 'Finish' button could not be found on the page.")

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", end_btn)
            time.sleep(0.5)
            end_btn.click()
            log.scrap("🏁 'Finish' button successfully clicked — redirection to the results page.")
        except Exception as e:
            log.warn(f"⚠️ Unable to click the 'Finish' button : {e}")


    except Exception as e:
        log.error(f"[QCM] Error inside solve_qcm : {e}")










def complete_module_exercises(driver, module_name):
    log.info(f"Exercise processing begins for the module: {module_name}")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "exercise-card"))
        )
        exercise_cards = driver.find_elements(By.CLASS_NAME, "exercise-card")

        log.scrap(f"{len(exercise_cards)} exercises found in module {module_name}")

        for i, card in enumerate(exercise_cards, start=1):
            try:
                title_elem = card.find_element(By.TAG_NAME, "h3")
                title = title_elem.text.strip()
                log.scrap(f"→ Exercise {i}: {title}")

                # ACCESS EXERCISES
                access_link = card.find_element(By.XPATH, ".//a[contains(@class,'exercise-card-link')]")
                driver.execute_script("arguments[0].scrollIntoView(true);", access_link)
                time.sleep(0.5)

                driver.execute_script("arguments[0].click();", access_link)
                log.scrap(f"Access to exercise {title} successfully.")

                #ACCESS QCM
                try:
                    log.debug("Waiting for QCM card to appear...")

                    # Wait for the block containing the MCQ button
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.ID, "mcq-cta-card"))
                    )
                    time.sleep(1)  # petit délai pour laisser le JS finir de charger

                    # Check if there is an iframe
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        driver.switch_to.frame(iframes[0])
                        log.debug("Switched into iframe containing QCM button.")

                    # Try several possible selectors for the button
                    possible_selectors = [
                        "//button[.//span[contains(translate(text(), 'ACCEDER AU QCM', 'acceder au qcm'),'acceder au qcm')]]",
                        "//span[contains(text(), 'Accéder au QCM')]/ancestor::button",
                        "//div[@id='mcq-cta-card']//button",
                    ]

                    qcm_button = None
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

                    log.scrap(f"Clicking the 'Access the quiz' button : {title}")

                    # Exit the iframe if necessary
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass

                    # Wait for the MCQ to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Valider')] | //form"))
                    )

                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/main/section/div/div/div[1]/div[2]/button"))
                    )
                    begin_btn = driver.find_element(By.XPATH, "/html/body/div/div/div/main/section/div/div/div[1]/div[2]/button")
                    begin_btn.click()
                    log.scrap(f"Multiple-choice questions loaded for: {title}")

                    #QCM SOLVER
                    solve_qcm(driver)

                except Exception as e:
                    log.warn(f"Unable to access the multiple-choice quiz for {title} : {e}")


            except Exception as e:
                continue

        log.info(f"All exercises in '{module_name}' successfully scraped and completed. ✅")

    except Exception as e:
        log.error(f"Error while scraping exercises : {e}")
