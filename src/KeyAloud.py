from pynput import keyboard
from gtts import gTTS
import playsound, os, json, time, sys
import logging

logging.basicConfig(
    filename="KeyAloud.log", format="%(asctime)s %(message)s", filemode="w"
)

logger = logging.getLogger("KeyAloud")
logger.level = 10
settings = json.load(open("settings.json", "rb"))
langsets = json.load(open("langsets.json", "rb"))

ignore = []
listener = None
active = False


def say(text: str):
    tts = gTTS(text, lang=settings["lang"])
    tts.save(os.environ["temp"] + "\\temp.mp3")
    playsound.playsound(os.environ["temp"] + "\\temp.mp3")
    os.remove(os.environ["temp"] + "\\temp.mp3")


def on_activate_deactivate():
    global listener
    global active
    if active:
        active = False
        listener.stop()
        logger.info("KeyAloud stopped")
        say(langsets[settings["lang"]]["stopped"])
    else:
        active = True
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        logger.info("KeyAloud started")
        say(langsets[settings["lang"]]["started"])


def on_end():
    global h
    listener.stop()
    h.stop()
    say(langsets[settings["lang"]]["ended"])
    logger.info("KeyAloud ended")
    sys.exit(0)


def on_press(key, *args):
    global ignore
    if key in ignore:
        return
    else:
        ignore.append(key)
    try:
        keyspeak = ""
        if key.__class__ == keyboard.KeyCode:
            if (
                settings["lang"] in langsets.keys()
                and str(key.vk) in langsets[settings["lang"]]["normal"].keys()
            ):
                keyspeak = langsets[settings["lang"]]["normal"][str(key.vk)]
            elif key.char != None:
                if (
                    settings["lang"] in langsets.keys()
                    and key.char in langsets[settings["lang"]]["chars"].keys()
                ):
                    keyspeak = langsets[settings["lang"]]["chars"][key.char]
                else:
                    keyspeak = key.char
            else:
                logger.warning(f"KeyCode with vk={key.vk} not found!")
                return
        else:
            if (
                settings["lang"] in langsets.keys()
                and f"{key}".replace("Key.", "")
                in langsets[settings["lang"]]["special"].keys()
            ):
                keyspeak = langsets[settings["lang"]]["special"][
                    f"{key}".replace("Key.", "")
                ]
            else:
                logger.warning(f"Key with name={key} not found!")
                return

        say(keyspeak)
    except playsound.PlaysoundException as e:
        time.sleep(0.5)
        on_press(key)
    except Exception as e:
        logger.exception(e)


def on_release(key, *args):
    global ignore
    try:
        ignore.remove(key)
    except Exception as e:
        logger.exception(e)


with keyboard.GlobalHotKeys(
    {
        "<ctrl>+<alt>+<shift>+k": on_activate_deactivate,
        "<ctrl>+<alt>+<shift>+e": on_end,
    }
) as h:
    on_activate_deactivate()
    h.join()
