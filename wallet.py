class Wallet:
    PLAY_COST = 10
    WIN_REWARD = 100
    MAX_RECHARGE = 114514
    def __init__(self, data=None):
        if data is None:
            self.balance = 0
            self.total_recharged = 0
            self.total_won = 0
            self.total_spent = 0
        else:
            self.balance = data.get("balance", 0)
            self.total_recharged = data.get("total_recharged", 0)
            self.total_won = data.get("total_won", 0)
            self.total_spent = data.get("total_spent", 0)

    def to_dict(self):
        return {
            "balance": self.balance,
            "total_recharged": self.total_recharged,
            "total_won": self.total_won,
            "total_spent": self.total_spent,
        }

    def recharge(self, amount):
        if amount <= 0:
            print("充值金额必须大于0。")
            return False
        if amount > self.MAX_RECHARGE:
            print(f"单次充值金额不能超过 {self.MAX_RECHARGE} 元。")
            return False
        self.balance += amount
        self.total_recharged += amount
        print(f"充值成功！已充值 {amount} 元，当前余额：{self.balance} 元")
        return True

    def can_play(self):
        return self.balance >= self.PLAY_COST

    def deduct_play_cost(self):
        if not self.can_play():
            print(f"余额不足！当前余额：{self.balance} 元，玩一次需要 {self.PLAY_COST} 元")
            return False
        self.balance -= self.PLAY_COST
        self.total_spent += self.PLAY_COST
        return True

    def add_win_reward(self):
        self.balance += self.WIN_REWARD
        self.total_won += self.WIN_REWARD
        print(f"恭喜获得 {self.WIN_REWARD} 元奖金！")

    def show_balance(self):
        print(f"\n--- 钱包信息 ---")
        print(f"当前余额：{self.balance} 元")
        print(f"累计充值：{self.total_recharged} 元")
        print(f"累计消费：{self.total_spent} 元")
        print(f"累计中奖：{self.total_won} 元")
        if self.total_spent > 0:
            net = self.total_won - self.total_spent
            if net >= 0:
                print(f"净收益：+{net} 元")
            else:
                print(f"净收益：{net} 元")

    def ask_recharge(self):
        while True:
            choice = input(f"\n余额不足，是否充值？(y/n)：").strip().lower()
            if choice == 'n':
                return False
            if choice == 'y':
                while True:
                    amount_str = input("请输入充值金额（元）：").strip()
                    if amount_str.isdigit():
                        amount = int(amount_str)
                        return self.recharge(amount)
                    print("请输入有效的正整数金额。")
            print("请输入 y 或 n。")
