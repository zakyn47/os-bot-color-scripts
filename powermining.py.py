import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from model.runelite_bot import BotStatus
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket
from utilities.geometry import RuneLiteObject


class PowerMiner(OSRSBot):
    def __init__(self):
        bot_title = "POWERMINER"
        description = "This bot powermine whatever is tagged by runelite with clr.PINK"
        super().__init__(bot_title=bot_title, description=description)
        self.running_time = 30
        self.take_breaks = False
        self.delay_lower = 1
        self.delay_upper = 5


    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_checkbox_option("take_breaks", "Take breaks?", [" "])
        self.options_builder.add_slider_option("delay_lower", " lower Delay between clicks (seconds)?", 1, 5)
        self.options_builder.add_slider_option("delay_upper", " upper Delay between clicks (seconds)?", 1, 5)

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "take_breaks":
                self.take_breaks = options[option] != []
            elif option == "delay_lower":
                self.delay = options[option]
            elif option == "delay_upper":
                self.delay = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Bot will{' ' if self.take_breaks else ' not '}take breaks.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        # Setup API
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        self.log_msg("Starting bot...")
        self.log_msg(f"API OK ? {api_m.test_endpoints()}")
        self.log_msg("Selecting inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        self.ores = 0
        failed_searches = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            marked_objects = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)

            if api_s.get_is_inv_full():
                self.drop(slots=api_s.get_inv_item_indices(ids.ores))

            for ore in marked_objects:
                self.ores += 1
                self.mouse.move_to(ore.random_point())
                self.mouse.click()
                time.sleep(rd.fancy_normal_sample(self.delay_lower, self.delay_upper))
                self.log_msg(f"ores mined : ~{self.ores}")

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.__logout("Finished.")

    def __logout(self, msg):
        self.log_msg(msg)
        self.logout()
        self.stop()

    def __drop_iron_ores(self, api_s: StatusSocket):
        """
        drops all iron ores from inventory
        """
        slots = api_s.get_inv_item_indices(ids.IRON_ORE)
        self.drop(slots)
        time.sleep(1)
