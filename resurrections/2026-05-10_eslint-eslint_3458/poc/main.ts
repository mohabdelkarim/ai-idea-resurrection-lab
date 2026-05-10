import * as path from 'path';
import * as require from 'require';
import { ConfigMerger } from './ConfigMerger';

class PluginResolver {
    private configMerger: ConfigMerger;

    constructor(configMerger: ConfigMerger) {
        this.configMerger = configMerger;
    }

    public resolvePlugins(config: any): void {
        if (config.dependencies) {
            config.dependencies.forEach((dependency: string) => {
                if (dependency.startsWith('eslint-plugin-')) {
                    this.resolvePlugin(dependency);
                }
            });
        }
    }

    private resolvePlugin(pluginName: string): void {
        try {
            require.resolve(pluginName);
            // Load the plugin
            require(pluginName);
        } catch (error) {
            if (error.code === 'MODULE_NOT_FOUND') {
                throw new Error(`Cannot find module '${pluginName}'`);
            } else {
                throw error;
            }
        }
    }
}

class ConfigMerger {
    public mergeConfigs(configs: any[]): any {
        // Simplified config merging logic for demonstration purposes
        return configs.reduce((mergedConfig, config) => ({ ...mergedConfig, ...config }), {});
    }
}

// Example usage:
const configMerger = new ConfigMerger();
const pluginResolver = new PluginResolver(configMerger);

const shareableConfig = {
    dependencies: ['eslint-plugin-no-use-extend-native'],
    rules: {
        'no-use-extend-native': 'error'
    }
};

pluginResolver.resolvePlugins(shareableConfig);

console.log('Plugins resolved successfully');