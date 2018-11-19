import React from 'react';
import "babel-polyfill";

import ReactDOM from 'react-dom';
import CssBaseline from '@material-ui/core/CssBaseline';

import AppBar from './AppBar.js';
import WorkFlow from './WorkFlow.js';

function App() {
  return (
    <React.Fragment>
      <CssBaseline />
      <AppBar />
      <WorkFlow />
    </React.Fragment>
  );
}

ReactDOM.render(<App />, document.querySelector('#app'));
