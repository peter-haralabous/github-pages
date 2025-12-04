# Webpack Setup

This document provides an overview of the Webpack setup for this project. Webpack is used to bundle our frontend
assets (JavaScript, CSS, etc.) for both development and production environments.

## Configuration Files

Our Webpack configuration is split into three files for better maintainability:

- `common.config.cjs`: This is the base configuration file that is used for both development and production. It defines
  the entry points, output paths, loaders (for TypeScript, JavaScript, Sass, and CSS), and common plugins.
- `dev.config.cjs`: This file contains settings specific to the development environment. It merges with
  `common.config.cjs` and adds features like source maps and the `webpack-dev-server` configuration. The dev server is
  configured to proxy backend requests to the Django development server.
- `prod.config.cjs`: This file contains settings for the production build. It also merges with `common.config.cjs` and
  includes optimizations like code minification and production-ready source maps.

## Key Features

- **Entry Points**: The main application code is located in `sandwich/static/js/project.js`, and vendor libraries are in
  `sandwich/static/js/vendors.js`.
- **Output**: Bundled files are generated in the `sandwich/static/webpack_bundles/` directory.
- **Backend Integration**: We use `webpack-bundle-tracker` to generate a `webpack-stats.json` file. This file allows our
  Django backend to automatically find and include the correct bundled asset files in the templates.
- **Styling**: The project uses [Sass](https://sass-lang.com/) and [Tailwind CSS](https://tailwindcss.com/). The loaders
  for these are configured in `common.config.cjs`.
- **JavaScript and TypeScript**: The project supports both JavaScript and TypeScript, which are transpiled using Babel.

## Development

To run the webpack development server, use the appropriate command from the project's `package.json` (e.g.,
`npm run start` or `yarn start`). The dev server will watch for file changes and automatically reload the browser.
