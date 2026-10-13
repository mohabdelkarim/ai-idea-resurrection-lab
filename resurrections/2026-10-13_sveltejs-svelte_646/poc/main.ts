import * as fs from 'fs';
import * as path from 'path';

// Simple ESTree‑like node definitions (subset needed for the demo)
interface BaseNode { type: string; }
interface Identifier extends BaseNode { type: 'Identifier'; name: string; }
interface Literal extends BaseNode { type: 'Literal'; value: string | number | boolean | null; }
interface TernaryExpression extends BaseNode { type: 'ConditionalExpression'; test: BaseNode; consequent: BaseNode; alternate: BaseNode; }
interface IfBlock extends BaseNode { type: 'IfBlock'; test: BaseNode; consequent: BaseNode[]; alternate?: BaseNode[]; }
interface ElementNode extends BaseNode { type: 'Element'; tagName: string; children: BaseNode[]; }

type Node = Identifier | Literal | TernaryExpression | IfBlock | ElementNode;

// Very small utility to clone nodes (shallow copy is enough for this PoC)
function clone<T extends Node>(node: T): T {
    return JSON.parse(JSON.stringify(node));
}

// Visitor interface – only the nodes we care about
interface Visitor {
    IfBlock?(node: IfBlock, parent: Node | null): Node | null;
}

// Traversal + transformation function
function traverse(node: Node, visitor: Visitor, parent: Node | null = null): Node {
    // Pre‑order visit
    if (visitor.IfBlock && node.type === 'IfBlock') {
        const replacement = visitor.IfBlock(node as IfBlock, parent);
        if (replacement) return replacement; // node replaced, skip children
    }
    // Recurse into children based on node type
    switch (node.type) {
        case 'IfBlock': {
            const ifNode = node as IfBlock;
            ifNode.consequent = ifNode.consequent.map(child => traverse(child, visitor, node));
            if (ifNode.alternate) {
                ifNode.alternate = ifNode.alternate.map(child => traverse(child, visitor, node));
            }
            break;
        }
        case 'Element': {
            const el = node as ElementNode;
            el.children = el.children.map(child => traverse(child, visitor, node));
            break;
        }
        // literals and identifiers have no children
    }
    return node;
}

// Optimisation visitor – converts simple IfBlock with single‑element branches into a ternary
function ifToTernaryVisitor(): Visitor {
    return {
        IfBlock(node: IfBlock, _parent: Node | null): Node | null {
            // Only optimise when both branches consist of a single Element with no further children
            if (node.consequent.length === 1 && node.alternate && node.alternate.length === 1) {
                const cons = node.consequent[0];
                const alt = node.alternate[0];
                if (cons.type === 'Element' && alt.type === 'Element') {
                    const ternary: TernaryExpression = {
                        type: 'ConditionalExpression',
                        test: clone(node.test),
                        consequent: clone(cons),
                        alternate: clone(alt)
                    } as any;
                    // Wrap the ternary in a parent element (e.g., <p>{...}</p>)
                    const wrapper: ElementNode = {
                        type: 'Element',
                        tagName: 'p',
                        children: [ternary]
                    };
                    return wrapper;
                }
            }
            return null; // no optimisation, keep original
        }
    };
}

// Example input AST mimicking the Svelte template from the issue
const exampleAst: ElementNode = {
    type: 'Element',
    tagName: 'div',
    children: [
        {
            type: 'IfBlock',
            test: { type: 'Identifier', name: 'foo' },
            consequent: [{ type: 'Element', tagName: 'p', children: [{ type: 'Literal', value: 'foo!' }] }],
            alternate: [{ type: 'Element', tagName: 'p', children: [{ type: 'Literal', value: 'not foo!' }] }]
        } as IfBlock
    ]
};

try {
    const optimized = traverse(exampleAst, ifToTernaryVisitor());
    const outPath = path.join(__dirname, 'optimized-ast.json');
    fs.writeFileSync(outPath, JSON.stringify(optimized, null, 2), 'utf-8');
    console.log('Optimisation complete. Output written to', outPath);
} catch (err) {
    console.error('Error during AST optimisation:', err);
    process.exit(1);
}