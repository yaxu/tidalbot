#!/bin/bash
startsc() {
   killall scsynth
   killall sclang
   tmux kill-session -t supercollider
   tmux new-session -s supercollider -d /usr/local/bin/sclang
   if [[ $? -eq 0 ]]; then
     echo tmux started
   else
     echo An error occurred starting tmux. RC was $?
   fi
}
/bin/pidof scsynth
if [[ $? -ne 0 ]]; then
  echo Creating scsynth
  startsc
fi
