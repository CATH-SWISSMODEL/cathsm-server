import React, { Component } from 'react';
import './App.css';

import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from './components/AppBar.js';
import WorkFlow from './components/WorkFlow.js';

class App extends Component {
  render() {
    return (
      <div className="App">
        <CssBaseline />
        <AppBar />
        <WorkFlow />
      </div>
    );
  }
}

export default App;
