import pandas as pd
import numpy as np
import datetime as dt
import os

data_dir = 'geolife-data/Data'
dirlist = os.listdir(data_dir)

label_dirs = []
for dir in dirlist[1:]:
  trajlist = os.listdir(data_dir + '/' + dir)
  if 'labels.txt' in trajlist:
    label_dirs.append(data_dir + '/' + dir)

traj_columns = ['latitude','longitude','height','days_total','date','time']

def year_plus(col):
  return col.replace(year=col.year + 1)

def get_trans_trip(record_dt,ref_df):
    time_fit = (record_dt >= ref_df['Start Time']) & (record_dt <= ref_df['End Time'])
    nmatch = time_fit.sum()
    if nmatch == 0:
        t_idx = None
    else:
        if nmatch > 1:
            print 'More than one mode match!'
        t_idx = ref_df.loc[time_fit].iloc[0].name
    return t_idx

match_paths = []
all_traj = pd.DataFrame()
for ldirs in label_dirs[:1]:
  print ldirs
  user = ldirs[-3:]
  trajpath = ldirs + '/Trajectory/'
  traj_files = os.listdir(trajpath)
  trip_trans = pd.read_csv(ldirs+'/labels.txt',sep='\t')
  trip_trans['Start Time'] = pd.to_datetime(trip_trans['Start Time'])
  trip_trans['End Time'] = pd.to_datetime(trip_trans['End Time'])
  #trip_trans['Start Time'] = trip_trans.apply(lambda x: year_plus(x['Start Time']),axis=1)
  #trip_trans['End Time'] = trip_trans.apply(lambda x: year_plus(x['End Time']),axis=1)
  trip_s_dates = trip_trans['Start Time'].dt.date.unique()
  trip_e_dates = trip_trans['End Time'].dt.date.unique()
  trip_a_dates = np.unique(np.append(trip_s_dates,trip_e_dates))
  for tf in traj_files:
    traj_df = (pd.read_csv(trajpath+tf
                            ,skiprows=6
                            ,usecols=[0,1,3,4,5,6]
                            ,names=traj_columns)
                .assign(record_dt = lambda x: pd.to_datetime(
                                        x['date'] + ' ' + x['time']
                                        ),
                        user = user
                        )
                )
    if traj_df['record_dt'].dt.date.isin(trip_a_dates).any():
        print 'matches possible'
        traj_df['trans_trip'] = traj_df.apply(lambda x: get_trans_trip(x.record_dt,trip_trans),axis=1)
        has_trip = ~(traj_df.trans_trip.isnull())
        traj_df['trans_mode'] = np.nan
        traj_df.loc[has_trip,'trans_mode'] = traj_df.loc[has_trip].apply(lambda x: trip_trans.loc[x.trans_trip,'Transportation Mode'],axis=1)
        all_traj = pd.concat([all_traj,traj_df])

all_traj.to_csv('_'.join(str(label_dirs),'trip','labeled.csv'))
