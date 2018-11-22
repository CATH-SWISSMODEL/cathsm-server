import React from "react";
import classNames from "classnames";
import PropTypes from "prop-types";
import { withStyles, createMuiTheme } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TablePagination from "@material-ui/core/TablePagination";
import TableRow from "@material-ui/core/TableRow";
import TableSortLabel from "@material-ui/core/TableSortLabel";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Paper from "@material-ui/core/Paper";
import Checkbox from "@material-ui/core/Checkbox";
import Button from "@material-ui/core/Button";
import Badge from "@material-ui/core/Badge";
import Chip from "@material-ui/core/Chip";
import IconButton from "@material-ui/core/IconButton";
import Radio from "@material-ui/core/Radio";
import Tooltip from "@material-ui/core/Tooltip";
import DeleteIcon from "@material-ui/icons/Delete";
import FilterListIcon from "@material-ui/icons/FilterList";
import { lighten } from "@material-ui/core/styles/colorManipulator";

import ScanMatchFigure from "./ScanMatchFigure";

function desc(a, b, orderBy) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

function stableSort(array, cmp) {
  const stabilizedThis = array.map((el, index) => [el, index]);
  stabilizedThis.sort((a, b) => {
    const order = cmp(a[0], b[0]);
    if (order !== 0) return order;
    return a[1] - b[1];
  });
  return stabilizedThis.map(el => el[0]);
}

function getSorting(order, orderBy) {
  return order === "desc"
    ? (a, b) => desc(a, b, orderBy)
    : (a, b) => -desc(a, b, orderBy);
}

const rows = [
  { id: "funfam", numeric: false, label: "Match" },
  { id: "description", numeric: false, label: "FunFam Description" },
  { id: "members", numeric: true, label: "Domains" },
  { id: "features", numeric: false, label: "Features" },
  { id: "query_region", numeric: false, label: "Location of matches" },
  { id: "evalue", numeric: true, label: "E-value" }
];

// FunfamMatchTableHead

class FunfamMatchTableHead extends React.Component {
  createSortHandler = property => event => {
    this.props.onRequestSort(event, property);
  };

  render() {
    const { order, orderBy, numSelected, rowCount } = this.props;

    return (
      <TableHead>
        <TableRow>
          {rows.map(row => {
            return (
              <TableCell
                key={row.id}
                numeric={row.numeric}
                padding={row.disablePadding ? "none" : "default"}
                sortDirection={orderBy === row.id ? order : false}
              >
                <Tooltip
                  title="Sort"
                  placement={row.numeric ? "bottom-end" : "bottom-start"}
                  enterDelay={300}
                >
                  <TableSortLabel
                    active={orderBy === row.id}
                    direction={order}
                    onClick={this.createSortHandler(row.id)}
                  >
                    {row.label}
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
            );
          }, this)}
        </TableRow>
      </TableHead>
    );
  }
}

FunfamMatchTableHead.propTypes = {
  onRequestSort: PropTypes.func.isRequired,
  order: PropTypes.string.isRequired,
  orderBy: PropTypes.string.isRequired,
  rowCount: PropTypes.number.isRequired
};

// FunfamMatchTableToolbar

const toolbarStyles = theme => ({
  root: {
    paddingRight: theme.spacing.unit
  },
  highlight:
    theme.palette.type === "light"
      ? {
          color: theme.palette.secondary.main,
          backgroundColor: lighten(theme.palette.secondary.light, 0.85)
        }
      : {
          color: theme.palette.text.primary,
          backgroundColor: theme.palette.secondary.dark
        },
  spacer: {
    flex: "1 1 100%"
  },
  actions: {
    color: theme.palette.text.secondary
  },
  title: {
    flex: "0 0 auto"
  }
});

let FunfamMatchTableToolbar = props => {
  const { numSelected, classes } = props;

  return (
    <Toolbar
      className={classNames(classes.root, {
        [classes.highlight]: numSelected > 0
      })}
    >
      <div className={classes.title}>
        {numSelected > 0 ? (
          <Typography color="inherit" variant="subtitle1">
            {numSelected} selected
          </Typography>
        ) : (
          <Typography variant="h6" id="tableTitle">
            Domain Matches
          </Typography>
        )}
      </div>
      <div className={classes.spacer} />
      <div className={classes.actions}>
        {numSelected > 0 ? (
          <Tooltip title="Delete">
            <IconButton aria-label="Delete">
              <DeleteIcon />
            </IconButton>
          </Tooltip>
        ) : (
          <Tooltip title="Filter list">
            <IconButton aria-label="Filter list">
              <FilterListIcon />
            </IconButton>
          </Tooltip>
        )}
      </div>
    </Toolbar>
  );
};

FunfamMatchTableToolbar.propTypes = {
  classes: PropTypes.object.isRequired,
  numSelected: PropTypes.number.isRequired
};

FunfamMatchTableToolbar = withStyles(toolbarStyles)(FunfamMatchTableToolbar);

// FunfamMatchList

const styles = theme => ({
  root: {
    width: "100%",
    marginTop: theme.spacing.unit * 1
  },
  table: {
    minWidth: 1020
  },
  tableWrapper: {
    overflowX: "auto"
  }
});

class FunfamMatchList extends React.Component {
  state = {
    order: "asc",
    orderBy: "evalue",
    selected: [],
    page: 0,
    rowsPerPage: 25
  };

  componentDidMount() {
    const { scanResult, queryId, querySequence } = this.props;
    this.setState({ scanResult, queryId, querySequence });
  }

  handleRequestSort = (event, property) => {
    const orderBy = property;
    let order = "desc";

    if (this.state.orderBy === property && this.state.order === "desc") {
      order = "asc";
    }

    this.setState({ order, orderBy });
  };

  handleClick = (event, id) => {
    const { selected } = this.state;
    const selectedIndex = selected.indexOf(id);
    let newSelected = [];

    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, id);
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1)
      );
    }

    this.setState({ selected: newSelected });
  };

  handleChangePage = (event, page) => {
    this.setState({ page });
  };

  handleChangeRowsPerPage = event => {
    this.setState({ rowsPerPage: event.target.value });
  };

  isSelected = id => this.state.selected.indexOf(id) !== -1;

  render() {
    const { classes } = this.props;
    const {
      scanResult,
      order,
      orderBy,
      selected,
      rowsPerPage,
      page,
      radio,
      queryId,
      querySequence
    } = this.state;
    const hits = scanResult ? scanResult.hits : [];
    const emptyRows =
      rowsPerPage - Math.min(rowsPerPage, hits.length - page * rowsPerPage);

    const data = hits.map(hit => {
      return {
        id: hit.matchId,
        funfam: hit.matchId,
        description: hit.matchDescription,
        members: hit.funfamMembers,
        uniq_ec_terms: hit.matchEcCount,
        uniq_go_terms: hit.matchGoCount,
        evalue: hit.significance,
        segments: hit.hsps.map((hsp, idx) => {
          return { id: idx, start: hsp.queryStart, end: hsp.queryEnd };
        })
      };
    });

    return (
      <Paper className={classes.root}>
        <FunfamMatchTableToolbar numSelected={selected.length} />
        <div className={classes.tableWrapper}>
          <Table className={classes.table} aria-labelledby="tableTitle">
            <FunfamMatchTableHead
              numSelected={selected.length}
              order={order}
              orderBy={orderBy}
              onRequestSort={this.handleRequestSort}
              rowCount={hits.length}
            />
            <TableBody>
              {stableSort(data, getSorting(order, orderBy))
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map(n => {
                  const isSelected = this.isSelected(n.id);
                  return (
                    <TableRow
                      hover
                      onClick={event => this.handleClick(event, n.id)}
                      role={radio ? "radio" : "checkbox"}
                      aria-checked={isSelected}
                      tabIndex={-1}
                      key={n.id}
                      selected={isSelected}
                    >
                      <TableCell component="th" scope="row">
                        {n.funfam}
                      </TableCell>
                      <TableCell>{n.description}</TableCell>
                      <TableCell>{n.members}</TableCell>
                      <TableCell>
                        {n.uniq_ec_terms && (
                          <Badge
                            badgeContent={n.uniq_ec_terms}
                            color="primary"
                            className={classes.ec}
                          >
                            <Chip label="EC" className={classes.ec} />
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <ScanMatchFigure
                          width={250}
                          residueLength={querySequence.length}
                          segments={n.segments}
                        />
                      </TableCell>
                      <TableCell numeric>{n.evalue}</TableCell>
                    </TableRow>
                  );
                })}
            </TableBody>
          </Table>
        </div>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={data.length}
          rowsPerPage={rowsPerPage}
          page={page}
          backIconButtonProps={{
            "aria-label": "Previous Page"
          }}
          nextIconButtonProps={{
            "aria-label": "Next Page"
          }}
          onChangePage={this.handleChangePage}
          onChangeRowsPerPage={this.handleChangeRowsPerPage}
        />
      </Paper>
    );
  }
}

FunfamMatchList.propTypes = {
  classes: PropTypes.object.isRequired,
  scanResult: PropTypes.object,
  queryId: PropTypes.string.isRequired,
  querySequence: PropTypes.string.isRequired
};

export default withStyles(styles)(FunfamMatchList);
