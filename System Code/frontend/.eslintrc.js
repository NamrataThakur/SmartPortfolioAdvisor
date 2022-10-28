module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'plugin:react/recommended',
    'airbnb',
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 12,
    sourceType: 'module',
  },
  plugins: [
    'react',
  ],
  rules: {
    "quote-props":0,
    "space-infix-ops":0,
    "prefer-template":0,
    "quotes":0,
    "comma-dangle":0,
    "no-trailing-spaces":0,
    "global-require":0,
    "eol-last":0,
    "import/newline-after-import":0,
    "import/order":0,
    "no-console": "off",
    "array-callback-return":0,
    "consistent-return":0,
    "no-mixed-spaces-and-tabs":0,
    "no-tabs":0,
    "no-undef":0,
    "no-param-reassign":0,
    "no-shadow":0,
    "no-plusplus":0,
    "no-useless-escape": 0,
    "no-nested-ternary": 0,
    "allowForLoopAfterthoughts": 0,
    "no-unused-vars": 0,
    "jsx-a11y/label-has-associated-control": [ 0, {
      "required": {
        "some": [ "nesting", "id"  ]
      }
    }],
    "react/button-has-type": 0,
    "import/no-cycle" :0,
    "import/no-extraneous-dependencies": [
      0, 
      {
        "devDependencies": false, 
        "optionalDependencies": false, 
        "peerDependencies": false
      }
    ],
    indent: ['off', 2],
    'react/function-component-definition': 0,
    'import/extensions': 0,
    'react/prop-types': 0,
    'linebreak-style': 0,
    'react/state-in-constructor': 0,
    'import/prefer-default-export': 0,
    'max-len': [
      2,
      550,
    ],
    'no-multiple-empty-lines': [
      'error',
      {
        max: 1,
        maxEOF: 1,
      },
    ],
    'no-underscore-dangle': [
      'error',
      {
        allow: [
          '_d',
          '_dh',
          '_h',
          '_id',
          '_m',
          '_n',
          '_t',
          '_text',
        ],
      },
    ],
    'object-curly-newline': 0,
    'react/jsx-filename-extension': 0,
    'react/jsx-one-expression-per-line': 0,
    'jsx-a11y/click-events-have-key-events': 0,
    'jsx-a11y/alt-text': 0,
    'jsx-a11y/no-autofocus': 0,
    'jsx-a11y/no-static-element-interactions': 0,
    'react/no-array-index-key': 0,
    'jsx-a11y/anchor-is-valid': [
      'error',
      {
        components: [
          'Link',
        ],
        specialLink: [
          'to',
          'hrefLeft',
          'hrefRight',
        ],
        aspects: [
          'noHref',
          'invalidHref',
          'preferButton',
        ],
      },
    ],
  },
};
