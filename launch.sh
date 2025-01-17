#!/bin/bash

#$1 train or test
#$2 agent type (ddpg, ppo, nav (for turtlebot3 navigation package)
#$3 load ep (optional)

# gnome-terminal -e "./launch/launch_env.sh $1 $2 $3 $4 $5 $6"
# sleep 4
# gnome-terminal -e "./launch/launch_agent.sh $1 $2 $3 $4 $5 $6"


# osascript -e "./launch/launch_env.sh $1 $2 $3 $4 $5 $6"
# sleep 4
# osascript -e "./launch/launch_agent.sh $1 $2 $3 $4 $5 $6"


# osascript -e 'tell application "Terminal" to do script "cd /Users/wen-chungcheng/catkin_noetic_ws/src/Autonav-Gym-Mod && conda activate ROS1_Noetic && ./launch/launch_env.sh '$1' '$2' '$3' '$4' '$5' '$6'"'
# sleep 4
# osascript -e 'tell application "Terminal" to do script "cd /Users/wen-chungcheng/catkin_noetic_ws/src/Autonav-Gym-Mod && conda activate ROS1_Noetic && ./launch/launch_agent.sh '$1' '$2' '$3' '$4' '$5' '$6'"'

osascript -e 'tell application "Terminal" to do script "cd /Users/wen-chungcheng/catkin_noetic_ws/src/Autonav-Gym-Mod && conda activate ROS1_Noetic && ./launch/launch_env.sh '$1' '$2' '$3' '$4' '$5' '$6' 2>&1 | tee /Users/wen-chungcheng/catkin_noetic_ws/src/Autonav-Gym-Mod/launch_env.log"'
sleep 4
# osascript -e 'tell application "Terminal" to do script "cd /Users/wen-chungcheng/catkin_noetic_ws/src/Autonav-Gym-Mod && conda activate ROS1_Noetic && ./launch/launch_agent.sh '$1' '$2' '$3' '$4' '$5' '$6' 2>&1 | tee /Users/wen-chungcheng/catkin_noetic_ws/src/Autonav-Gym-Mod/launch_agent.log"'
