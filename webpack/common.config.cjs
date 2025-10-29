const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  target: 'web',
  context: path.join(__dirname, '../'),
  entry: {
    vendors: path.resolve(__dirname, '../sandwich/static/js/vendors'),
    project: {
      import: path.resolve(__dirname, '../sandwich/static/js/project'),
      dependOn: 'vendors',
    },
    survey: {
      import: path.resolve(__dirname, '../sandwich/static/js/survey'),
      dependOn: 'vendors',
    },
  },
  output: {
    path: path.resolve(__dirname, '../sandwich/static/webpack_bundles/'),
    publicPath: '/static/webpack_bundles/',
    filename: 'js/[name]-[fullhash].js',
    chunkFilename: 'js/[name]-[fullhash].js',
  },
  plugins: [
    new BundleTracker({
      path: path.resolve(path.join(__dirname, '../')),
      filename: 'webpack-stats.json',
    }),
    new MiniCssExtractPlugin({ filename: 'css/[name].[contenthash].css' }),
  ],
  module: {
    rules: [
      // we pass the output from babel loader to react-hot loader
      {
        test: /\.[tj]sx?$/,
        loader: 'babel-loader',
      },
      {
        test: /\.s?css$/i,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: ['@tailwindcss/postcss'],
              },
            },
          },
        ],
      },
    ],
  },
  resolve: {
    modules: ['node_modules'],
    extensions: ['.ts', '.tsx', '.js', '.jsx'],
  },
  optimization: {
    // Use a single runtime chunk so shared modules are deduped into common runtime
    runtimeChunk: 'single',
  },
};
