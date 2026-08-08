from concurrent.futures import thread
import time
import random
from core.resou import read_resources, should_attack
from core.actions import (
    click_when_found,
    click,
    deploy_hero,
    deploy_spell
)
from zoom import LDZoom
from core.camera import run_ld_macro
from wall import *
from core.adb import deploy, swipe, tap
from account.account_manager import AccountManager
import zoom
def sleep_interruptible(thread, seconds):
    end = time.time() + seconds

    while time.time() < end:
        if check_stop(thread):
            return False

        time.sleep(0.1)

    return True
def check_stop(thread):
    return not thread.running


def run_once(bot, config, thread):
    profile_name = config.get("_profile_name", "Default")
    raw_actions = config.get("deploy_actions", [])
    active_actions = [a for a in raw_actions if a.get("enabled", True)]

    thread.write_log(
        f"[BATTLE START] Current Profile: {profile_name} | "
        f"Mode: LIVE DEPLOY | "
        f"Active Actions: {len(active_actions)}"
    )

    heroes = config.get("heroes", {})
    loot_enable = config.get("loot_enable", True)
    min_gold = config.get("min_gold", 200000)
    min_elixir = config.get("min_elixir", 200000)
    loot_mode = config.get("loot_mode", "AND")

    wall_enable = config.get("wall_enable", False)
    wall_resource = config.get("wall_resource", "Auto")
    wall_count = config.get("wall_count", 4)
    attack_side = config.get("attack_side", "Random")
    deploy_delay = config.get("deploy_delay", 5)
    return_home_delay = config.get("return_home_delay", 5)
    
    if not sleep_interruptible(thread, 3):
        return False

    #ZOOM OUT 
    #thread.write_log("Running Zoom Macro (F8)...")
    #run_ld_macro("LDPlayer")
    if not sleep_interruptible(thread, 2):
        return False
    thread.write_log(f"{bot.name} - Bắt đầu tìm trận")

# Vào trận
    if check_stop(thread):
        return False
    
    if wall_enable:
        if not sleep_interruptible(thread, 5):
            return False
        if wall_resource == "Auto":
            if gold_full(bot.device):
                if check_stop(thread):
                    return False
                upgrade_gold(bot.device,wall_count,thread)
            elif elixir_full(bot.device):
                upgrade_elixir(bot.device,wall_count,thread)

        elif wall_resource == "Gold":
            if gold_full(bot.device):
                upgrade_gold(bot.device,wall_count,thread)

        elif wall_resource == "Elixir":
            if elixir_full(bot.device):
                upgrade_elixir(bot.device,wall_count,thread)

    if not click_when_found(bot.device,"attack_button", timeout=2,stop_check=lambda: not thread.running):
        print("Không thấy Attack Button, thử Return Home...")
        if check_stop(thread):
            return False
        if click(bot.device,"return_home"):
            if not sleep_interruptible(thread, 3):
                return False
            return False
        click(bot.device,"attack")
        
    if not sleep_interruptible(thread, 0.8):
        return False
    tap(bot.device,266,677)
    #if not click_when_found(bot.device,"find_match", timeout=5,stop_check=lambda: not thread.running):
    #    print("Không tìm thấy Find Match")
    #    click(bot.device,"return_home")
    if not sleep_interruptible(thread, 1):
        return False
    if not click_when_found(bot.device,"attack",timeout=3,stop_check=lambda: not thread.running):
        return False
    if not sleep_interruptible(thread, 0.5):
        return False

    if loot_enable:

        while True:

            if not sleep_interruptible(thread, 5):
                return False

            resources = read_resources(bot.device)

            thread.write_log(
            f"Gold: {resources['gold']} | "
            f"Elixir: {resources['elixir']}"
                )

            if should_attack(
            resources,
            min_gold,
            min_elixir,
            loot_mode
        ):  
                thread.attack_count += 1
                thread.attack_changed.emit(thread.attack_count)
                thread.write_log("Base đạt yêu cầu.")
                break

            thread.write_log("Base không đạt -> Find Next")

            if not click_when_found(bot.device, "find_next", timeout=3,threshold=0.7,stop_check=lambda: not thread.running):
                print("Không bấm được Find Next")
                return False
    

    if not sleep_interruptible(thread, 0.5):
        return False
    swipe(bot.device,775,544,770,120,300)
    
    random_mode = config.get("random_mode", "Sequential")
    random_configs = config.get("random_configs", [])
    enabled_configs = [c for c in random_configs if c.get("enabled", True) and c.get("deploy_actions")]

    if enabled_configs:
        if random_mode == "Random":
            selected_cfg = random.choice(enabled_configs)
        else:
            seq_idx = getattr(thread, "strategy_seq_index", 0) % len(enabled_configs)
            selected_cfg = enabled_configs[seq_idx]
            thread.strategy_seq_index = seq_idx + 1

        cfg_name = selected_cfg.get("name", "Strategy Config")
        raw_actions = selected_cfg.get("deploy_actions", [])
        thread.write_log(f"[STRATEGY] Selected Strategy Config: '{cfg_name}' (Mode: {random_mode})")
    else:
        raw_actions = config.get("deploy_actions", [])

    deploy_actions = [a for a in raw_actions if a.get("enabled", True)]

    thread.write_log(f"[BATTLE START] Current Profile: {profile_name} | Mode: LIVE DEPLOY ({len(deploy_actions)} active actions)")

    if deploy_actions:
        thread.write_log(f"[LIVE DEPLOY] Executing {len(deploy_actions)} deployment sequence actions...")
        for idx, action in enumerate(deploy_actions, 1):
            if check_stop(thread):
                return False

            unit_id = action.get("unit_id", "dragon")
            unit_name = action.get("unit_name", unit_id)
            tag = action.get("tag", "")
            x = action.get("x", 800)
            y = action.get("y", 450)
            delay = float(action.get("delay", 0.5))
            repeat_count = int(action.get("repeat_count", 1))

            tag_str = f"[{tag}] " if tag else ""
            thread.write_log(f"[ACTION #{idx}] {tag_str}{unit_name} -> Tap at ({x}, {y}) x{repeat_count}, delay {delay}s")

            for r in range(repeat_count):
                if check_stop(thread):
                    return False
                tap(bot.device, x, y)
                if repeat_count > 1:
                    time.sleep(0.08)

            if not sleep_interruptible(thread, delay):
                return False
    else:
        thread.write_log("[LIVE DEPLOY] ⚠️ No active deployment actions configured in action list.")

    # Return home after battle execution
    tap(bot.device, 100, 675)
    thread.write_log(f"Chờ Return Home Delay: {return_home_delay}s...")
    if not sleep_interruptible(thread, return_home_delay):
        return False
    tap(bot.device, 1000, 590)
    if not click_when_found(bot.device, "return_home", timeout=10):
        print("Không tìm thấy nút trở về")
        return

    print("Hoàn thành!")
    return True