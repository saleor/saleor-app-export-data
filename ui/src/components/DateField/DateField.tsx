import React from 'react'
import dayjs from 'dayjs'
import { TextField, Box } from '@material-ui/core'

import useStyles from './style'

interface DateFieldProps {
  setDate: (newDate: string) => void
  setTime: (newTime: string) => void
  time: string
  date: string
}

export enum Format {
  time = 'HH:mm',
  date = 'yyyy-MM-DD',
}

export function DateField(props: DateFieldProps) {
  const { setDate, setTime, date, time } = props
  const classes = useStyles()

  return (
    <Box className={classes.dateBox}>
      <TextField
        className={classes.date}
        type="date"
        label="Date"
        value={date}
        defaultValue={dayjs().format(Format.date)}
        onChange={e =>
          setDate(dayjs(new Date(e.currentTarget.value)).format(Format.date))
        }
      />
      <TextField
        className={classes.time}
        type="time"
        label="Time"
        value={time}
        defaultValue={dayjs().format(Format.time)}
        onChange={e => {
          setTime(e.currentTarget.value)
        }}
      />
    </Box>
  )
}

export default DateField
