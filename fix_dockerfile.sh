#!/bin/bash
# ––∫—––ø—Ç –¥–ª— –———Ç—–æ––æ –—–ø—–∞–≤–ª–µ–Ω–— Dockerfile –Ω–∞ —–µ—–≤–µ—–µ

# ––µ—–µ—–æ–¥ –≤ –¥–—–µ–∫—Ç–æ—–— –ø—–æ–µ–∫—Ç–∞
cd ~/facy-app || cd /home/ubuntu/facy-app || exit 1

# ––æ–∑–¥–∞–Ω––µ —–µ–∑–µ—–≤–Ω–æ–π –∫–æ–ø––
cp Dockerfile Dockerfile.backup

# –ó–∞–º–µ–Ω–∞ libgl1-mesa-glx –Ω–∞ libgl1
sed -i 's/libgl1-mesa-glx/libgl1/g' Dockerfile

echo " Dockerfile –—–ø—–∞–≤–ª–µ–Ω!"
echo "–¢–µ–ø–µ—— –∑–∞–ø—É——Ç–—Ç–µ: docker compose build"

