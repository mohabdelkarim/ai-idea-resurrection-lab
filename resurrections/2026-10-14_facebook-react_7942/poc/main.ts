import * as fs from 'fs';
import * as path from 'path';

// Simplified Fiber node interface mirroring React's internal structure
export interface FiberNode {
  tag: number; // identifies the type of component
  key: string | null;
  type: any; // component type (function, class, host)
  stateNode: any; // rendered output (DOM node, etc.)
  child: FiberNode | null;
  sibling: FiberNode | null;
  return: FiberNode | null; // parent link
  pendingProps: any;
  memoizedProps: any;
  // ... other fields are omitted for brevity
}

/**
 * FiberSchema mirrors the internal Fiber structure and provides a helper
 * to serialize a node into a markdown-friendly representation.
 */
export class FiberSchema {
  static serialize(node: FiberNode): string {
    const tagName = FiberSchema.tagToString(node.tag);
    const key = node.key !== null ? `key="${node.key}" ` : '';
    return `- ${tagName} ${key}(type: ${typeof node.type})`;
  }

  private static tagToString(tag: number): string {
    // Simplified mapping; real React has many tags
    switch (tag) {
      case 0:
        return 'FunctionComponent';
      case 1:
        return 'ClassComponent';
      case 2:
        return 'HostComponent';
      case 3:
        return 'HostText';
      default:
        return 'Unknown';
    }
  }
}

/**
 * Traverses a Fiber tree using the singly‑linked list algorithm (no recursion).
 * Emits a markdown string representing the hierarchy.
 */
export function traverseFiber(root: FiberNode): string {
  let result = '# Fiber Tree\n';
  const stack: {node: FiberNode; depth: number}[] = [{node: root, depth: 0}];

  while (stack.length > 0) {
    const {node, depth} = stack.pop()!;
    const indent = '  '.repeat(depth);
    result += `${indent}${FiberSchema.serialize(node)}\n`;

    // Push siblings first so that children are processed before them (LIFO)
    if (node.sibling) {
      stack.push({node: node.sibling, depth});
    }
    if (node.child) {
      stack.push({node: node.child, depth: depth + 1});
    }
  }

  return result;
}

/**
 * Generates documentation files under docs/fiber based on the provided root fiber.
 */
export function generateDocs(root: FiberNode): void {
  const outputDir = path.resolve(__dirname, 'docs', 'fiber');
  try {
    fs.mkdirSync(outputDir, {recursive: true});
  } catch (e) {
    console.error('Failed to create output directory:', e);
    return;
  }

  const markdown = traverseFiber(root);
  const outPath = path.join(outputDir, 'FiberTree.md');
  try {
    fs.writeFileSync(outPath, markdown, 'utf8');
    console.log('Fiber documentation generated at', outPath);
  } catch (e) {
    console.error('Error writing documentation file:', e);
  }
}

/**
 * Example usage: construct a tiny fiber tree and run the generator.
 */
function example(): void {
  const leaf: FiberNode = {
    tag: 3,
    key: null,
    type: 'span',
    stateNode: null,
    child: null,
    sibling: null,
    return: null,
    pendingProps: null,
    memoizedProps: null,
  };

  const child: FiberNode = {
    tag: 2,
    key: 'child1',
    type: 'div',
    stateNode: null,
    child: leaf,
    sibling: null,
    return: null,
    pendingProps: null,
    memoizedProps: null,
  };

  const root: FiberNode = {
    tag: 0,
    key: 'root',
    type: () => null,
    stateNode: null,
    child,
    sibling: null,
    return: null,
    pendingProps: null,
    memoizedProps: null,
  };

  // Link parent references (optional for this demo)
  child.return = root;
  leaf.return = child;

  generateDocs(root);
}

// Execute example when run directly
if (require.main === module) {
  try {
    example();
  } catch (err) {
    console.error('Unexpected error during execution:', err);
  }
}