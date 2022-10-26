import asyncio
from asyncio import sleep

from pynput import keyboard

from galaxy_express import GalaxyExpress


def check_keyboard_events() -> tuple[bool, str | None]:
    with keyboard.Events() as keyboard_events:
        keyboard_event = keyboard_events.get(0.1)
        if not keyboard_event:
            return False, None
        key = keyboard_event.key
        if key == keyboard.Key.esc:
            return True, None
        if hasattr(key, 'char'):
            s = input()
            return False, s
        return False, None


async def listen_console_input(g: GalaxyExpress) -> None:
    eof = False
    while not eof:
        eof, input_s = check_keyboard_events()
        if input_s:
            await g.get_request(input_s)
        await sleep(0.05)
    g.finished = True
    await g.package_sending_finish()
    print('EOF')
    exit(1)


async def run(loop) -> None:
    g = GalaxyExpress()
    task_processing = loop.create_task(g.process_send_packages())
    task_listen = loop.create_task(listen_console_input(g))
    await asyncio.gather(task_processing, task_listen)


def main() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))


if __name__ == "__main__":
    main()
