import json
import os


class Configure:
    def __init__(self):
        dir_path = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(dir_path, "configure.json")
        print(self.path)
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.data = data

    def get(self, bot, name):
        if bot in self.data:
            if name in self.data[bot]:
                return self.data[bot][name]
            else:
                return None
        else:
            return None


# configure = Configure()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "config.json")
    print(path)
