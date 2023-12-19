from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pywinmacro as pw
import urllib.request
import pickle


room_dict = {
}

member_names = [
]

driver = webdriver.Chrome()

# 잔디 로그인
driver.get("https://{your_team}.jandi.com/landing/kr/signin")

login_field = driver.find_element(By.CLASS_NAME, "SigninForm_formContainer__5CPCJ").find_elements(By.TAG_NAME, "input")
time.sleep(1)
login_field[0].send_keys("{id}")
time.sleep(1)
login_field[1].send_keys("{ps}", Keys.ENTER)
time.sleep(2)

driver.get("https://{your_team}.jandi.com/")


# 슬랙 로그인
driver.execute_script("window.open('https://{your_team}.slack.com/sign_in_with_password')")
time.sleep(1)
driver.switch_to.window(driver.window_handles[-1])

time.sleep(1)
id_field = driver.find_element(By.ID, "email")
id_field.send_keys("{id}")

time.sleep(1)
ps_field = driver.find_element(By.ID, "password")
ps_field.send_keys("{ps}!", Keys.ENTER)

time.sleep(1)
driver.get("https://{your_team}.slack.com")

driver.switch_to.window(driver.window_handles[0])


# room select
room_list = driver.find_elements(By.CLASS_NAME, "lnb-list-item._topicItem.desktop-room-context")

for room_element in room_list:
    thread = False
    try:
        room_element.find_element(By.CLASS_NAME, "icon-ic-board.fn-15.lnb-inline-icon.flex-fix")
        thread = True
    except:
        pass

    room_name = room_element.text
    if room_name not in room_dict.keys():
        continue

    room_element.click()

    OUT_MESSAGES = []
    txts = []
    previous_messages_text = ""
    latest_date = ""
    new_classes = []
    new_cls = []
    counter = 0
    for i in range(100):
        messages = driver.find_elements(By.XPATH, '//*[@id="chat-messages"]/*')

        txt = messages[0].text.split("\n")[0].strip()
        if previous_messages_text == txt:
            pw.click((3057, 482))
            time.sleep(1)
            pw.mouse_upscroll(3000)
            counter += 1
            if counter >= 5:
                break
            time.sleep(3)
            continue
        else:
            previous_messages_text = txt
            counter = 0

        out_messages = []
        for message in messages:
            time.sleep(0.3)
            cls = message.get_attribute("class")
            txt = message.text
            if txt in txts:
                continue
            else:
                txts.append(txt)

            # 날짜 메시지
            if cls == 'system-message date-divider _message present':
                txt = txt.replace("년 ", ".")
                txt = txt.replace("월 ", ".")
                txt = txt.replace("일 ", ". (")
                txt = txt.replace("요일", ")")
                latest_date = txt
                continue
            else:
                msg_time = message.find_elements(By.TAG_NAME, "time")
                if msg_time:
                    msg_time = msg_time[0].get_attribute("data-write-time")
                line = ""

            # 시스템 메시지
            if cls == 'system-message noti _message present':
                line = txt

                if msg_time:
                    line += "\n(" + latest_date + " " + msg_time + ")"

            # 일반 메시지
            elif cls == 'message text _message present' or cls == 'message text self _message present':
                name = txt[:4].strip()
                content = txt[4:].strip()
                name = "[" + name + "]"
                for el in member_names:
                    if el in content:
                        content.replace(el, "@" + el)

                line = name + "\n"
                line += content
                if msg_time:
                    line += "    (" + latest_date + " " + msg_time + ")"

            # 이모티콘
            elif cls == 'message text sticker _message present':
                name = "[" + txt.strip() + "]"
                sticker = message.find_element(By.CLASS_NAME, "sticker")
                line = name + "\n"
                filename = "imoge/" + line.strip().replace(" ", "") + ".png"
                sticker.screenshot(filename)
                line += "\n<" + filename + ">"

                if msg_time:
                    line += "    (" + latest_date + " " + msg_time + ")"

            # 연속 메시지
            elif cls in ('message text text-child self _message present', 'message text text-child text-split _message present', 'message text text-child _message present', 'message text text-child text-split self _message present'):
                for el in member_names:
                    if el in txt:
                        txt.replace(el, "@" + el)

                if out_messages:
                    line = out_messages.pop()
                else:
                    continue
                line += "\n" + txt

                if msg_time:
                    line += "    (" + latest_date + " " + msg_time + ")"

            # 연속 메시지_이모티콘
            elif cls == 'message text text-child sticker self _message present':
                line = out_messages.pop()
                sticker = message.find_element(By.CLASS_NAME, "sticker")
                filename = line.split("\n")[0].strip().replace(" ", "") + ".png"
                sticker.screenshot("imoge/" + filename)
                line += "\n<" + filename + ">"
                if msg_time:
                    line += "    (" + latest_date + " " + msg_time + ")"

            # 대댓글
            elif cls == 'non-selectable _message present':
                # 원본 댓글
                origin_content = message.find_elements(By.CLASS_NAME, "message.thread")
                if origin_content:
                    message = origin_content[0]

                    origin_name = message.find_element(By.CLASS_NAME, "card-inf-wrap").text.strip().replace("\n", " (") + ")"
                    origin_content = message.find_element(By.CLASS_NAME, "card-inf-2").text

                    line = "[원본 메시지]\n" + origin_name + "\n" + origin_content + "\n\n"

                    comment = message.find_elements(By.CLASS_NAME, "msg-container.comment.only-thred")
                    if comment:
                        comment = comment[0]
                        text = comment.text

                        line += "[댓글]\n"

                        name = txt[:4].strip()
                        content = txt[4:].strip()
                        name = "[" + name + "]"
                        for el in member_names:
                            if el in content:
                                content.replace(el, "@" + el)

                        msg_time = comment.find_elements(By.TAG_NAME, "time")
                        if msg_time:
                            msg_time = msg_time[0].get_attribute("data-write-time")

                        line += name + "\n"
                        line += content
                        if msg_time:
                            line += "    (" + latest_date + " " + msg_time + ")"
                else:
                    line = out_messages.pop()
                    line += "\n" + message.text
                    msg_time = message.find_elements(By.TAG_NAME, "time")
                    if msg_time:
                        msg_time = msg_time[0].get_attribute("data-write-time")
                        line += "    (" + latest_date + " " + msg_time[0] + ")"

            # 사진 첨부
            elif cls in ("message text videochat filegroup self _message present", 'message text videochat filegroup _message present'):
                name = txt[:4].strip()
                content = txt[4:].strip()
                name = "[" + name + "]"
                for el in member_names:
                    if el in content:
                        content.replace(el, "@" + el)

                line = name + "\n"
                line += content
                if msg_time:
                    line += "    (" + latest_date + " " + msg_time + ")"

                imgs = message.find_elements(By.TAG_NAME, "img")[1:]
                for img in imgs:
                    url = img.get_attribute("src").split("?")[0]
                    filename = "photo/" + str(time.time()) + ".png"
                    urllib.request.urlretrieve(url, filename)
                    line += "\n<" + filename + ">"
            else:
                new_classes.append(cls)
                new_cls.append((cls, message))
                break

            if line and line not in out_messages:
                line = line.replace("- 회의중", "")
                line = line.replace("\n\n", "\n")
                out_messages.append(line)
                print(line)

        counter = 0
        for el in OUT_MESSAGES:
            if el not in out_messages:
                out_messages.append(el)
                counter += 1
        if counter == 0 and OUT_MESSAGES:
            print(2)
            break
        else:
            OUT_MESSAGES = out_messages.copy()

    with open(room_name + ".pkl", "wb") as file:
        pickle.dump(OUT_MESSAGES, file)


# 슬랙에 올리기
driver.switch_to.window(driver.window_handles[-1])
while OUT_MESSAGES:
    line = OUT_MESSAGES[0]
    textarea = driver.find_element(By.CLASS_NAME, "ql-editor.ql-blank")
    line = line.replace("\n(2023", "(2023")
    line = line.replace("\n1", "")
    line = line.replace("\u200d", "")
    line = line.replace("👍️", "")
    line = line.replace("🥑️", "")
    line = line.replace("👨", "")
    line = line.replace("👦", "")
    line = line.replace("\n\n", "\n")
    line = line.replace("\n\n", "\n")

    splt = line.split("\n")
    for token in splt:
        token = token.strip()
        if token:
            if "<" not in token:
                for el in member_names:
                    token = token.replace(el, "@" + el)
                    token = token.replace("@@", "@")
                textarea.send_keys(token, Keys.ENTER)
                time.sleep(0.1)
            else:
                filename = 'C:\\Users\\needl\\Desktop\\slack migration\\' + token[1:-1].replace("/", "\\")
                upload_button = driver.find_element(By.CLASS_NAME, "p-shortcuts_menu_trigger_button_container--composer_ia_icon_button")
                upload_button.click()
                time.sleep(0.5)
                my_comp_button = driver.find_element(By.XPATH, '//*[@id="shortcuts_menu_select_option_6"]/span/div')
                my_comp_button.click()
                time.sleep(3)
                pw.type_in(filename)
                pw.key_press_once("enter")
                textarea.send_keys(Keys.ENTER)

    OUT_MESSAGES = OUT_MESSAGES[1:]
