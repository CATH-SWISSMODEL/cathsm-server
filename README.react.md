
# Django / React

https://www.valentinog.com/blog/tutorial-api-django-rest-react/#Django_REST_with_React_what_you_will_learn

Get up to date node / npm

```
brew install node
brew install npm
```

```
npm init -y
npm i webpack webpack-cli --save-dev
```


```
# package.json
"scripts": {
    "dev": "webpack --mode development ./cathapi/frontend/src/index.js --output ./cathapi/frontend/static/frontend/main.js",
    "build": "webpack --mode production ./cathapi/frontend/src/index.js --output ./cathapi/frontend/static/frontend/main.js"
}
```

```
npm i @babel/core babel-loader @babel/preset-env @babel/preset-react babel-plugin-transform-class-properties --save-dev
npm i react react-dom prop-types --save-dev
```

```
# .babelrc
{
    "presets": [
        "@babel/preset-env", "@babel/preset-react"
    ],
    "plugins": [
        "transform-class-properties"
    ]
}
```

```
# webpack.config.js
module.exports = {
    module: {
    rules: [
        {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
            loader: "babel-loader"
        }
        }
    ]
    }
};
```
