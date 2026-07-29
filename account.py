import json
import os
import datetime
from wallet import Wallet

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")


class AccountManager:
    def __init__(self, data_file=DATA_FILE, leaderboard_file=LEADERBOARD_FILE):
        self.data_file = data_file
        self.leaderboard_file = leaderboard_file
        self.users = {}
        self.current_username = None
        self._load()

    def _load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.users = json.load(f)
            except (json.JSONDecodeError, OSError):
                self.users = {}
        else:
            self.users = {}

    def _save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"保存用户数据失败：{e}")
        self._save_leaderboard()

    def _rank_data(self):
        rows = []
        for name, data in self.users.items():
            wallet = data.get("wallet", {})
            stats = data.get("stats", {})
            total_won = wallet.get("total_won", 0)
            total_spent = wallet.get("total_spent", 0)
            total_wins = stats.get("total_wins", 0)
            total_plays = stats.get("total_plays", 0)
            win_rate = (total_wins / total_plays * 100) if total_plays > 0 else 0
            net = total_won - total_spent
            rows.append({
                "username": name,
                "total_wins": total_wins,
                "total_plays": total_plays,
                "win_rate": round(win_rate, 2),
                "net_profit": net,
                "balance": wallet.get("balance", 0),
                "total_recharged": wallet.get("total_recharged", 0),
                "total_won_money": total_won,
                "total_spent_money": total_spent,
            })
        return rows

    def _save_leaderboard(self, top_n=100):
        rows = self._rank_data()
        by_wins = sorted(rows, key=lambda r: (r["total_wins"], r["net_profit"]), reverse=True)
        ranked = []
        for i, r in enumerate(by_wins, 1):
            entry = dict(r)
            entry["rank"] = i
            if i == 1:
                entry["medal"] = "金"
            elif i == 2:
                entry["medal"] = "银"
            elif i == 3:
                entry["medal"] = "铜"
            else:
                entry["medal"] = None
            ranked.append(entry)
        snapshot = {
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_users": len(by_wins),
            "top_n": min(top_n, len(by_wins)),
            "sort_by": "total_wins DESC, net_profit DESC",
            "leaderboard": ranked[:top_n],
        }
        try:
            with open(self.leaderboard_file, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"保存排行榜失败：{e}")

    def load_leaderboard_snapshot(self):
        if not os.path.exists(self.leaderboard_file):
            return None
        try:
            with open(self.leaderboard_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _ensure_user(self, username):
        if username not in self.users:
            self.users[username] = {
                "wallet": {
                    "balance": 0,
                    "total_recharged": 0,
                    "total_won": 0,
                    "total_spent": 0,
                },
                "stats": {
                    "total_plays": 0,
                    "total_wins": 0,
                },
            }
            print(f"\n新用户 \"{username}\" 已注册！")
            self._save()
            return True
        return False

    def login(self):
        print("\n" + "=" * 30)
        print("          用户登录              ")
        print("=" * 30)
        while True:
            username = input("请输入用户名：").strip()
            if not username:
                print("用户名不能为空，请重新输入。")
                continue
            self.current_username = username
            is_new = self._ensure_user(username)
            print(f"\n欢迎回来，{username}！")
            if is_new:
                print("这是您的首次登录，祝您游戏愉快！")
            return is_new

    def get_wallet(self):
        if not self.current_username:
            raise RuntimeError("尚未登录")
        wallet_data = self.users[self.current_username].get("wallet", {})
        return Wallet(wallet_data)

    def get_stats(self):
        if not self.current_username:
            raise RuntimeError("尚未登录")
        stats = self.users[self.current_username].get("stats", {})
        return stats.get("total_plays", 0), stats.get("total_wins", 0)

    def save_state(self, wallet, total_plays, total_wins):
        if not self.current_username:
            raise RuntimeError("尚未登录")
        self.users[self.current_username]["wallet"] = wallet.to_dict()
        self.users[self.current_username]["stats"] = {
            "total_plays": total_plays,
            "total_wins": total_wins,
        }
        self._save()

    def has_balance(self):
        if not self.current_username:
            return False
        bal = self.users[self.current_username].get("wallet", {}).get("balance", 0)
        return bal > 0

    def logout(self):
        self.current_username = None

    def show_leaderboard(self, top_n=10):
        self._save_leaderboard(top_n=max(top_n, 100))
        snapshot = self.load_leaderboard_snapshot()
        rows = self._rank_data()
        if not rows:
            print("\n暂无排行数据。")
            return

        title = "抽奖排行榜 TOP " + str(min(top_n, len(rows)))
        width = 100
        print()
        print("=" * width)
        print(title.center(width))
        if snapshot:
            sub = f"生成时间：{snapshot.get('generated_at', '-')}    共 {snapshot.get('total_users', len(rows))} 位用户"
            print(sub.center(width))
        print("=" * width)
        header = (
            f"{'排名':<8}"
            f"{'用户名':<20}"
            f"{'中奖次数':>12}"
            f"{'游玩次数':>12}"
            f"{'胜率(%)':>10}"
            f"{'净收益(元)':>14}"
            f"{'余额(元)':>12}"
        )
        print(header)
        print("-" * width)

        by_wins = sorted(rows, key=lambda r: (r["total_wins"], r["net_profit"]), reverse=True)
        display = by_wins[:top_n]
        for i, r in enumerate(display, 1):
            if i == 1:
                rank_str = f"{i} [金]"
            elif i == 2:
                rank_str = f"{i} [银]"
            elif i == 3:
                rank_str = f"{i} [铜]"
            else:
                rank_str = f"{i}"
            name = r["username"]
            if len(name) > 18:
                name = name[:16] + ".."
            net = r["net_profit"]
            net_str = f"+{net}" if net >= 0 else f"{net}"
            line = (
                f"{rank_str:<8}"
                f"{name:<20}"
                f"{r['total_wins']:>12}"
                f"{r['total_plays']:>12}"
                f"{r['win_rate']:>10.1f}"
                f"{net_str:>14}"
                f"{r['balance']:>12}"
            )
            if self.current_username and r["username"] == self.current_username:
                line += "     <-- 我"
            print(line)

        me = None
        if self.current_username:
            for i, r in enumerate(by_wins, 1):
                if r["username"] == self.current_username:
                    me = (i, r)
                    break
        if me:
            rank, r = me
            print("-" * width)
            msg = (
                f"您的排名：第 {rank} 名    "
                f"中奖 {r['total_wins']} 次    "
                f"净收益 {r['net_profit']} 元    "
                f"当前余额 {r['balance']} 元"
            )
            print(msg.center(width))
        print("=" * width)
        if snapshot:
            info = f"排行榜快照已保存至: {self.leaderboard_file}"
            print(info.center(width))
