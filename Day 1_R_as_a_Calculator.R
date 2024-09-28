rm(list = ls()) # initialization, always put this line at the beginning

###########################Class Intro##############################
# Watch my Intro Videos on Canvas
# Check
# 1. Quick Start Guide and Syllabus on Canvas
# 2. Quiz/HW/Group Practice: on Canvas > Calendar, Course Summery, To do
# 3. Piazza: discuss questions online
# 4. Canvas: Check your grades, download my lecture code, etc.



#############################R Intro################################
# install R
# always choose the latest version!
# usually runs behind screen



##########################RStudio Intro#############################
# install RStudio
# RStudio is an user interface of R, or to be exact, an integrated development environment (IDE)
# save/edit/debug .R file



#############################Arithmetic#############################
# run each line and guess/watch the output on the console

8 + 17
8 - 3
8 * 3; 8 / 3; 8 ^ 2 # 3 operations in one line, separated by ;

8 ^ (1/3) # power, to be precise, cubic root

8 / 3; 8 %/% 3 # different quotients: regular and integer
# for advanced students: try 8 / (-3); 8 %/% (-3)

8 %% 3 # remainder 
# for advanced students: try 8 %% (-3)



########################Calculator functions########################

exp(2); 2.718281828459 ^ 2
e = 2.718281828459; e^2 # Are they the same?


log(7.389056)

?log # IMPORTANT TRICK: using ? for help documentation
     # like help("log") or help('log')

log(9, base = 3); log(9) # different output because of different bases!
log(9, 3) # too brief, not recommended
log(x = 9, base = 3) # best way to call a function with parameters by name


e <- exp(1); log(e^2) 
e = 2.718281828459; log(e^2) # What is the base here? The default one, check its help
e; print(e) # same output


sin(pi/2); cos(pi/2); tan(pi/2) # using radian, not degree; output: not zero or infinity
pi # preset constant


sqrt(4); sqrt(-4); 4/0 # NaN & Inf for undefined values
?NaN
?Inf



########################Other easy functions########################
# To know the meaning of the following functions, always use ?

abs(4); abs (-4); abs(0)


floor(2.5); floor(-2.5)
8 / 3; 8 %/% 3 
8 / (-3); 8 %/% (-3)
ceiling(2.5); ceiling(-2.5)


round(8000/3, 10) # 8000/3 = 2666.667
round(8000/3, 0); round(8000/3, -2)


signif(8000/3, 2)
signif(8000/3, 5)



######################Statistics distributions######################
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!IMPORTANT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Check http://onlinestatbook.com/2/introduction/distributions.html if your stats is rusty

?dnorm
# Pay attention to the first letter:   
# d - density (pdf)
# p - probability (cdf) (which side?!!)
# q - quantile (critical value, or inverse of cdf) (which side?)
# r - random generating

dnorm(0); dnorm(0, 0, 1) # pdf; see details at http://onlinestatbook.com/2/calculators/normal_dist.html
pnorm(q = -1, 1)         # cdf
qnorm(0.5, 10, 2)        # z-critical value from the left, be careful about the sidedness here!!!
rnorm(20, 0, 0.1)
rnorm(20, 0, 0.1)        # different random number every time!



?distribution # find all the distribution commands
?dt
dt(0, 1000) # cf. dnorm(0)
pt(0, 10)



##########################Miscellaneous#############################

?cot
??cot # ?? gets more search results.
??cotangent # no such function => try this useful formula: cot(pi/2) = 1 / tan(pi/2)
??hypergeometric # like help.search("hypergeometric") or help.search('hypergeometric')

x = -1; y <- 3 # <- means assignment, like =, but better than =
x
y

ls()

rm(x) # delete x from the memory
ls()
x

rm(list = ls()) # delete all the vars from the memory
ls()
y


# Set/Get Working Directory
# see motivation in http://onlinestatbook.com/2/calculators/normal_dist.html

setwd("C:/Users/BY/STAT303/code") # like setwd('C:/Users/BY/STAT303/code') 
# It works on my computer, not on your computer!
# change it accordingly.
getwd()

setwd("..") # like setwd('..')
getwd(); list.files() # list all files in your working directory

setwd("code") # like setwd('code')
getwd(); list.files()


# IMPORTANT: Always set up your working directory at first, then there is no hassle to find your files.

# You can use Menu: Session > Set Working Directory to do the same job as setwd()


# Try to generate a .R file in the working directory, then use it below
source("2Vector.R") # like source('2vector.R')

demo(graphics)
demo(plotmath)

q() # like quit()



############################Shortcuts###############################

# up/down arrow         : previous/next command (on console)
# ESC                   : interrupt current command
# Ctrl + Enter (PC)     : Run the script line by line or from the selected part (very important!)
# F1                    : Get help for the selected part (very important!)
# Alt + - (PC)          : <- (assignment)
# Ctrl + Shift + c      : comment/decomment all the selected lines
# Ctrl + Shift + h (PC) : set up the working directory
# Ctrl + Z              : Undo
# Ctri + Shift + Z      ; Redo

# For Mac, google "RStudio shortcut for Mac"



############################Summary#################################

# Preview before the class is very important!

# R is interpreted line by line, unlike C++.

# Set up the working dir and save .R and data files in the correct dir.

# Function(): repeated code, call/invoke it with parameters.

# How to find the help:
# 1. use ? or ?? in R
# 2. Google R subject or error message, very important!
# 3. Discuss it on Piazza
# 4. Contact my TA or me

# Understanding statistical distribution is even more important than coding in this course.