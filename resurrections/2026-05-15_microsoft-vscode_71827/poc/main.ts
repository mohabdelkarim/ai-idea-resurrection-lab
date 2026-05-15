import * as fs from 'fs';
import * as path from 'path';
import { createCanvas, loadImage } from 'canvas';

const ICON_SIZE = 256;
const OUTPUT_FILE = 'output.png';

async function generateIcon() {
  try {
    const iconImage = await loadImage('input.png');
    const canvas = createCanvas(ICON_SIZE, ICON_SIZE);
    const ctx = canvas.getContext('2d');

    // Draw the icon with a Fluent Design-aligned style
    ctx.fillStyle = '#0078d4';
    ctx.fillRect(0, 0, ICON_SIZE, ICON_SIZE);

    // Add depth to the icon
    ctx.shadowBlur = 10;
    ctx.shadowOffsetX = 5;
    ctx.shadowOffsetY = 5;
    ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';

    ctx.drawImage(iconImage, 50, 50, ICON_SIZE - 100, ICON_SIZE - 100);

    // Save the icon as a PNG file
    const out = fs.createWriteStream(OUTPUT_FILE);
    const stream = canvas.createPNGStream();
    stream.pipe(out);
    out.on('finish', () => console.log('Icon generated: ' + OUTPUT_FILE));
  } catch (error) {
    console.error('Error generating icon:', error);
  }
}

generateIcon();