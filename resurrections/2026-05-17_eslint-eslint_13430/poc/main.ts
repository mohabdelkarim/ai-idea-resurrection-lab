import { TSESTree } from '@typescript-eslint/experimental-utils';
import { createRule } from 'eslint';
import { isIdentifier, isMemberExpression, isOptionalMemberExpression } from 'eslint/utils/ast-utils';

const create = (context) => {
  const sourceCode = context.getSourceCode();

  return {
    'Identifier' : (node) => {
      if (isIdentifier(node)) {
        const parent = node.parent;
        if (isMemberExpression(parent) && parent.object === node) {
          const propertyName = sourceCode.getText(parent.property);
          if (parent.property.type === 'Identifier') {
            const optionalChaining = sourceCode.getText(parent) + '?.' + propertyName;
            context.report({
              node: parent,
              message: 'prefer optional chaining',
              suggest: [
                {
                  desc: 'Change to optional chaining',
                  fix: (fixer) => fixer.replaceNode(parent, optionalChaining),
                },
              ],
            });
          }
        }
      }
    },
    'LogicalExpression' : (node) => {
      if (node.operator === '&&') {
        const left = node.left;
        const right = node.right;
        if (isIdentifier(left) || isMemberExpression(left)) {
          if (isIdentifier(right) || isMemberExpression(right)) {
            const optionalChaining = sourceCode.getText(left) + '?.' + sourceCode.getText(right);
            context.report({
              node: node,
              message: 'prefer optional chaining',
              suggest: [
                {
                  desc: 'Change to optional chaining',
                  fix: (fixer) => fixer.replaceNode(node, optionalChaining),
                },
              ],
            });
          }
        }
      }
    },
    'ConditionalExpression' : (node) => {
      const test = node.test;
      const consequent = node.consequent;
      const alternate = node.alternate;
      if (test.type === 'BinaryExpression' && test.operator === '!=' && test.left.type === 'Identifier' && test.left.name === 'obj' && test.right.type === 'NullLiteral') {
        if (consequent.type === 'MemberExpression' && alternate.type === 'Identifier' && alternate.name === 'undefined') {
          const optionalChaining = sourceCode.getText(test.left) + '?.' + sourceCode.getText(consequent.property);
          context.report({
            node: node,
            message: 'prefer optional chaining',
            suggest: [
              {
                desc: 'Change to optional chaining',
                fix: (fixer) => fixer.replaceNode(node, optionalChaining),
              },
            ],
          });
        }
      }
    },
  };
};

export const rule = createRule({
  create,
  name: 'prefer-optional-chaining',
  meta: {
    docs: {
      description: 'disallow use of && and ? : for optional chaining',
    },
    messages: {
      preferOptionalChaining: 'prefer optional chaining',
    },
    type: 'suggestion',
    schema: [],
  },
  defaultOptions: [],
});