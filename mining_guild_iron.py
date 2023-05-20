import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class MiningGuildIron(OSRSBot):
    def __init__(self):
        bot_title = "Mining guild - iron ore"
        description = "mining and banking iron ore in the mining guild, set bank to deposit all, mark bank clr.yellow and iron rocks clr.pink, make sure both are visible in win.game_view"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during UI-less testing)
        self.running_time = 50

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def __bank(self, api_m: MorgHTTPSocket):
        self.mouse.move_to(destination=self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)[0].random_point())
        self.mouse.click()
        time.sleep(5)
        self.mouse.move_to(self.win.inventory_slots[0].random_point())
        self.mouse.click()
        self.mouse.move_to(destination=self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)[0].random_point())
        self.mouse.click()
        api_m.wait_til_gained_xp(skill="Mining", timeout=8)

    def main_loop(self):
        """
        Bot main loop.
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.
        """
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        mined_ores = 0
        gained_xp = 0
        
        
        self.log_msg(f"API_M OK? : {api_m.test_endpoints()}")
        self.log_msg("STARTING BOT")
        self.mouse.move_to(self.win.cp_tabs[3].random_point())
        self.mouse.click()

        start_time = time.time()
        end_time = self.running_time * 60

        while time.time() - start_time < end_time:
            iron_rocks = self.get_all_tagged_in_rect(self.win.game_view, clr.PINK)
            bank_deposit = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
            iron_ore = api_m.get_first_occurrence(item_id=ids.IRON_ORE)
            starting_point = self.get_nearest_tag(clr.PURPLE)

            if api_s.get_is_inv_full():
                self.log_msg("Inventory full, banking...")
                self.__bank(api_m=api_m)
            else:
                for rock in iron_rocks:
                    self.mouse.move_to(destination=rock.random_point())
                    self.mouse.click()
                    api_m.wait_til_gained_xp(skill="Mining", timeout=2)
                    mined_ores += 1
                    gained_xp += 35

            self.update_progress((time.time() - start_time) / end_time)
            self.log_msg(f"Runtime: {round((time.time() - start_time) / 60, 2)} minutes")
            self.log_msg(f"Mined ores: {mined_ores}")
            self.log_msg(f"Gained xp: {gained_xp}")

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()