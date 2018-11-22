import React from "react";
import PropTypes from "prop-types";
import { withStyles } from "@material-ui/core/styles";

const styles = theme => ({
  root: {
    position: "relative",
    display: "block",
    height: 2,
    "background-color": "#ddd"
  },
  hsp: {
    height: 7,
    position: "absolute",
    "background-color": "#c00"
  }
});

class ScanMatchFigure extends React.Component {
  render() {
    const { classes, width, residueLength, segments } = this.props;
    const resPerPixel = residueLength / width;
    const style = { width };

    return (
      <div className={classes.root} style={style}>
        {segments.map(n => {
          const { id, start, end } = n;
          const w = (end - start) * resPerPixel;
          const l = start * resPerPixel;
          const spanStyle = { width: w + "%", left: l + "%" };
          console.log("ScanMatchFigure.style: ", n, spanStyle);
          return <span key={id} style={spanStyle} />;
        })}
      </div>
    );
  }
}

ScanMatchFigure.defaultProps = {
  width: 250
};

ScanMatchFigure.propTypes = {
  classes: PropTypes.object.isRequired,
  residueLength: PropTypes.number.isRequired,
  segments: PropTypes.array.isRequired,
  width: PropTypes.number.isRequired
};

export default withStyles(styles)(ScanMatchFigure);
