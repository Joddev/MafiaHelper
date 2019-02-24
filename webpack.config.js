var path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
    entry: './webpack/src/main/app.js',
    output: {
        filename: 'index.js',
        path: path.resolve(__dirname, './game/static/game/js')
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        },
        extensions: ['*', '.js', '.vue', '.json']
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.css$/,
                use: ['vue-style-loader', 'css-loader']
            },
        ]
    },
    plugins: [
        // make sure to include the plugin!
        new VueLoaderPlugin()
    ]
};
