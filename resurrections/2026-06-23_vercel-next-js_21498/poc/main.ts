import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { promises as fs } from 'fs';
import { fileURLToPath } from 'url';

const middleware = async (req: NextRequest) => {
  const { pathname } = req.url;
  const path = fileURLToPath(new URL(pathname, 'file://'));
  const dir = join(process.cwd(), 'pages');
  const files = await fs.readdir(dir);
  const matchingFile = files.find((file) => file.toLowerCase() === path.toLowerCase().split('/').pop());
  if (matchingFile) {
    const correctPath = pathname.toLowerCase();
    if (correctPath !== pathname) {
      return new NextResponse(null, {
        status: 301,
        headers: {
          Location: correctPath,
        },
      });
    }
  }
  return new NextResponse(null, { status: 200 });
};

export default middleware;

// Error handling
try {
  // Your middleware logic here
} catch (error) {
  console.error(error);
  return new NextResponse(null, { status: 500 });
}