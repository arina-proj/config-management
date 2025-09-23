commands="cd ./
ls
cd test_vfs
cd level1
ls
cd level2
ls  
cd level3
ls
cd ../../..
cd .  
ls
exit"

echo "$commands" | python3 lab2.py --path . --prompt "MyVFS "