import React, { Component } from 'react';
import './App.css';

import CssBaseline from '@material-ui/core/CssBaseline';
import Container from '@material-ui/core/Container';
import WorkFlow from './components/WorkFlow.js';

class App extends Component {
  render() {
    return (
      <div className="App">
        <CssBaseline />
        <Container>
          <WorkFlow />
        </Container>
      </div>
    );
  }
}

export default App;
