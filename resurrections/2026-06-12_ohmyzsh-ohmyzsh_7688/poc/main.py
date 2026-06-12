import os
import sys

class PluginLoader:
    def __init__(self, plugins_dir, plugin_name):
        self.plugins_dir = plugins_dir
        self.plugin_name = plugin_name

    def load_plugin(self):
        plugin_path = os.path.join(self.plugins_dir, self.plugin_name)
        if os.path.exists(plugin_path):
            print(f"Loading plugin: {self.plugin_name}")
            return True
        else:
            print(f"Warning: plugin {self.plugin_name} not found")
            return False

class OhMyZshConfig:
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.plugins_dir = os.path.join(config_dir, "plugins")

    def load_plugins(self, plugin_names):
        for plugin_name in plugin_names:
            loader = PluginLoader(self.plugins_dir, plugin_name)
            loader.load_plugin()

def main():
    config_dir = os.path.expanduser("~/.oh-my-zsh")
    ohmyzsh_config = OhMyZshConfig(config_dir)

    plugin_names = ["zsh-syntax-highlighting", "zsh-autosuggestions"]
    ohmyzsh_config.load_plugins(plugin_names)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)