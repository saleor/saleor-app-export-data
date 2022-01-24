import React, { useEffect, useReducer, useState, useRef } from 'react'
import { Paper } from '@material-ui/core'

import { useMutationDeleteReport } from '../../api/export/mutation'
import { useQueryReports } from '../../api/export/query'
import TableHeader from '../../components/TableHeader'
import { ReportTable } from '../../components/ReportTable/ReportTable'
import { reportsReducer, initialReports } from './reducer'
import useStyles from './style'

export function ReportList() {
  const classes = useStyles()
  const headerRef = useRef<HTMLDivElement>(null)
  const [state, dispatch] = useReducer(reportsReducer, initialReports)
  const [page, setPage] = useState(0)
  const [reportsPerPage, setReportsPerPage] = useState(10)
  const [pureReports, refetchPureReports] = useQueryReports(
    {
      first: 25,
      after: state.navigation.endCursor,
    },
    { pause: true, requestPolicy: 'network-only' }
  )
  const [, deleteReportMutation] = useMutationDeleteReport()

  const reset = () => {
    dispatch({ type: 'SET_TOTAL', total: 0 })
    dispatch({ type: 'SET_REPORTS', reports: [] })
    dispatch({
      type: 'SET_NAVIGATION',
      navigation: { endCursor: '', hasNext: true },
    })
  }

  const deleteSelectedReports = async () => {
    // TODO: implement delete reports
  }

  const deleteReport = async (id: number) => {
    const response = await deleteReportMutation({ reportId: id })

    if (response.data && response.data.deleteReport.errors.length === 0) {
      reset()
      refetchPureReports()
    }
  }

  useEffect(() => {
    if (pureReports.data && !pureReports.fetching) {
      dispatch({
        type: 'SET_REPORTS',
        reports: [
          ...state.reports,
          ...pureReports.data.reports.edges.map(({ node }) => ({
            isSelected: false,
            id: node.id,
            entity: node.type,
            recipients: 20,
            name: node.name,
          })),
        ],
      })
      dispatch({
        type: 'SET_NAVIGATION',
        navigation: {
          hasNext: pureReports.data.reports.pageInfo.hasNext,
          endCursor: pureReports.data.reports.pageInfo.endCursor,
        },
      })
      dispatch({
        type: 'SET_TOTAL',
        total: pureReports.data.reports.totalCount,
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pureReports])

  useEffect(() => {
    if (state.navigation.hasNext) refetchPureReports()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.navigation.endCursor])

  return (
    <Paper className={classes.paper}>
      <div ref={headerRef}>
        <TableHeader />
      </div>
      <ReportTable
        deleteSelectedReports={deleteSelectedReports}
        deleteReport={deleteReport}
        unselectAllReports={() => dispatch({ type: 'UNSELECT_ALL' })}
        selectAllReports={() => dispatch({ type: 'SELECT_ALL' })}
        toggleReport={id => dispatch({ type: 'TOGGLE_REPORT', id: id })}
        reports={state.reports}
        count={state.total}
        page={page}
        setPage={page => {
          setPage(page)
        }}
        rowsPerPage={reportsPerPage}
        setRowsPerPage={rowsPerPage => {
          reset()
          setPage(0)
          setReportsPerPage(rowsPerPage)
        }}
        subtract={headerRef.current?.clientHeight}
      />
    </Paper>
  )
}

export default ReportList