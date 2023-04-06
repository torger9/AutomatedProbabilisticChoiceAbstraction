% proccess datafile
% First clear all text from datafile using command :%s/\a\|\.\|(\|)//g in vim
% Additionally, remove last line (possible incomplete) with command :$d
% format: (locations solved) (total heap size) (size difference) (objects created)  (unaccessable)
%         (largest 3 objects with names)(largest created object and name)

data = load("../src_test/data.txt");

locationsSolved = data(:,1);
totalHeapSize   = data(:,2);
sizeDifference  = data(:,3);
objectsCreated  = data(:,4);
unaccessable    = data(:,5);
top3_1          = data(:,6);
top3_2          = data(:,7);
top3_3          = data(:,8);
%largest         = data(:,9); %This line is redundant (same as top3_1) 

clear data;


n = 1:1:length(locationsSolved);

figure
hold on
plot(n,locationsSolved, 'm')
plot(n, totalHeapSize, 'k')
plot(n, sizeDifference, 'c')
plot(n, top3_1, 'r')
plot(n, top3_2, 'g')
plot(n, top3_3, 'b')

figure 
plot(n,objectsCreated,'k')

figure
plot(n, unaccessable, 'm')