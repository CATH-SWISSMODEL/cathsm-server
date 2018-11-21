import React from 'react';
import classNames from 'classnames';
import PropTypes from 'prop-types';
import { withStyles, createMuiTheme } from '@material-ui/core/styles';

const styles = theme => ({
  root: {
    position: "relative",
    height: 2,
    "background-color": '#ddd',
  },
  hsp: {
    height: 7,
    position: "absolute",
    "background-color": '#c00',
  }
});

class ScanMatchFigure extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      selected: []
    };
  }

  render() {
    const { classes, width, residueLength, segments } = this.props;

    const resPerPixel = residueLength / width;
    const style = { width };

    return (
      <div className={classes.root} style={style}>
        {segments.map( n => {
          const spanStyle = {
            width: (n.end - n.start) * resPerPixel,
            left: (n.start) * resPerPixel,
          };
          return <span key={n.id} style={spanStyle} />
        })}
      </div>
    );
  }
}

ScanMatchFigure.propTypes = {
  classes: PropTypes.object.isRequired,
  residueLength: PropTypes.number.isRequired,
  segments: PropTypes.array.isRequired,
  width: PropTypes.number.isRequired,
};

export default withStyles(styles)(ScanMatchFigure);
