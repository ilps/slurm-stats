sacct --starttime 2021-01-01 --format=User,JobID,Jobname,jobidraw,partition,state,time,submit,start,end,elapsed,MaxRss,MaxVMSize,nnodes,ncpus,nodelist,alloctres,totalcpu --parsable2 --allusers --units=G > sacct_stats.csv