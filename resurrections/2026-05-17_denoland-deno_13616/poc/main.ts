import * as fs from 'fs';
import * as path from 'path';

interface FmtOptions {
  useSemicolon: boolean;
}

class DenoFmt {
  private readonly options: FmtOptions;

  constructor(options: FmtOptions) {
    this.options = options;
  }

  public format(filePath: string): void {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const formattedContent = this.formatContent(fileContent);
    fs.writeFileSync(filePath, formattedContent);
  }

  private formatContent(content: string): string {
    const config = this.getDprintConfig();
    // Simulate dprint formatting with the provided config
    // For demonstration purposes, just remove semicolons if asi is true
    if (config.asi) {
      content = content.replace(/;/g, '');
    }
    return content;
  }

  private getDprintConfig(): { asi: boolean } {
    return {
      asi: !this.options.useSemicolon,
    };
  }
}

function main(): void {
  try {
    const args = process.argv.slice(2);
    if (args.length !== 2) {
      console.error('Usage: deno fmt <file_path>');
      process.exit(1);
    }
    const filePath = args[0];
    const options: FmtOptions = {
      useSemicolon: false, // Default to false for demonstration
    };
    const denoFmt = new DenoFmt(options);
    denoFmt.format(filePath);
    console.log(`Formatted file: ${filePath}`);
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();