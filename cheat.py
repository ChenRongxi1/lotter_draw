class CheatMode:
    ACTIVATION_CODE = "88224646BA"
    ALLOWED_USER = "ChenRongxi"
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._enabled = False
            cls._instance._current_username = None
        return cls._instance

    def __init__(self):
        pass

    def set_username(self, username):
        self._current_username = username
        if self._enabled and not self._is_allowed():
            self._enabled = False

    def _is_allowed(self):
        return self._current_username == self.ALLOWED_USER

    def is_activation_code(self, user_input):
        return user_input == self.ACTIVATION_CODE

    def activate(self):
        if not self._is_allowed():
            print("\n【系统提示】权限不足，无法启用维护模式。")
            return False
        self._enabled = True
        print("\n【系统提示】维护模式已激活。")
        return True

    def deactivate(self):
        self._enabled = False
        print("\n【系统提示】维护模式已关闭。")
        return True

    def is_enabled(self):
        return self._enabled and self._is_allowed()

    def generate_winning_number(self, user_number):
        if self.is_enabled():
            return user_number
        return None

    def toggle(self):
        if self._enabled:
            return self.deactivate()
        else:
            return self.activate()
