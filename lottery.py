import random
from wallet import Wallet
from cheat import CheatMode
from account import AccountManager


def get_user_number(cheat):
    while True:
        user_input = input("请输入一个5位数：").strip()
        if cheat.is_activation_code(user_input):
            cheat.toggle()
            continue
        if len(user_input) == 5 and user_input.isdigit():
            return int(user_input)
        print("输入无效，请输入一个5位数字。")


def generate_winning_number(user_number, cheat):
    forced = cheat.generate_winning_number(user_number)
    if forced is not None:
        return forced
    return random.randint(10000, 99999)


def check_result(user_num, winning_num):
    print(f"\n您的号码：{user_num:05d}")
    print(f"中奖号码：{winning_num:05d}")
    if user_num == winning_num:
        print("\n【恭喜您！中奖了！】")
        return True
    else:
        print("\n【很遗憾，没有中奖。下次再试试运气吧！】")
        return False


def ask_play_again():
    while True:
        choice = input("\n是否再玩一次？(y/n)：").strip().lower()
        if choice in ('y', 'n'):
            return choice == 'y'
        print("请输入 y 或 n。")


def ask_manual_recharge(wallet):
    while True:
        choice = input("\n是否充值？(y/n)：").strip().lower()
        if choice == 'n':
            return
        if choice == 'y':
            while True:
                amount_str = input("请输入充值金额（元）：").strip()
                if amount_str.isdigit():
                    amount = int(amount_str)
                    wallet.recharge(amount)
                    return
                print("请输入有效的正整数金额。")
        print("请输入 y 或 n。")


def show_main_menu():
    print("\n" + "=" * 30)
    print("          主菜单              ")
    print("=" * 30)
    print("  1. 登录并开始游戏")
    print("  2. 查看排行榜")
    print("  3. 退出")
    while True:
        choice = input("请选择 [1-3]：").strip()
        if choice in ('1', '2', '3'):
            return choice
        print("请输入 1、2 或 3。")


def ask_post_game_menu():
    print("\n" + "-" * 30)
    print("  1. 查看排行榜")
    print("  2. 返回主菜单")
    while True:
        choice = input("请选择 [1-2]：").strip()
        if choice == '1':
            return 'leaderboard'
        if choice == '2':
            return 'quit'
        print("请输入 1 或 2。")


def run_game(account):
    total_plays, total_wins = account.get_stats()
    no_history = (total_plays == 0 and total_wins == 0)
    is_new_or_empty = no_history and not account.has_balance()

    cheat = CheatMode()
    cheat.set_username(account.current_username)
    wallet = account.get_wallet()

    print(f"\n当前用户：{account.current_username}")
    wallet.show_balance()
    print(f"\n历史游玩次数：{total_plays}，历史中奖次数：{total_wins}")

    if is_new_or_empty:
        print("\n当前没有余额，需要先充值才能游玩！")
        ask_manual_recharge(wallet)
        account.save_state(wallet, total_plays, total_wins)
    else:
        print("\n检测到已有余额，直接开始游戏！")
        account.save_state(wallet, total_plays, total_wins)

    while True:
        if not wallet.can_play():
            if not wallet.ask_recharge():
                break

        if not wallet.deduct_play_cost():
            break

        total_plays += 1
        print(f"\n--- 第 {total_plays} 轮 ---")
        print(f"扣除 {Wallet.PLAY_COST} 元，剩余余额：{wallet.balance} 元")

        user_number = get_user_number(cheat)
        winning_number = generate_winning_number(user_number, cheat)
        won = check_result(user_number, winning_number)

        if won:
            total_wins += 1
            wallet.add_win_reward()

        print(f"\n--- 抽奖统计 ---")
        print(f"游玩次数：{total_plays}")
        print(f"中奖次数：{total_wins}")
        wallet.show_balance()

        account.save_state(wallet, total_plays, total_wins)

        if not ask_play_again():
            break

    account.save_state(wallet, total_plays, total_wins)

    print("\n" + "=" * 30)
    print("          游戏结束              ")
    print(f"  用户：{account.current_username}  ")
    print(f"  共游玩 {total_plays} 次，中奖 {total_wins} 次  ")
    wallet.show_balance()
    print("=" * 30)


def main():
    print("=" * 30)
    print("     欢迎来到抽奖程序     ")
    print("=" * 30)
    print(f"游戏规则：每玩一次花费 {Wallet.PLAY_COST} 元，中奖可得 {Wallet.WIN_REWARD} 元")

    while True:
        account = AccountManager()
        menu_choice = show_main_menu()

        if menu_choice == '3':
            print("感谢使用，再见！")
            return

        if menu_choice == '2':
            account.show_leaderboard()
            continue

        if menu_choice == '1':
            account.login()
            run_game(account)
            post = ask_post_game_menu()
            if post == 'leaderboard':
                account.show_leaderboard()
            print("已返回主菜单。")


if __name__ == "__main__":
    main()
