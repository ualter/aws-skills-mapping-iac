#!/bin/bash

set -o errexit

Reset='\033[0m'
Black='\033[0;30m' 
Red='\033[0;31m'   
Green='\033[0;32m' 
Yellow='\033[0;33m'
Blue='\033[0;34m'  
Purple='\033[0;35m'
Cyan='\033[0;36m'  
White='\033[0;37m' 
# Intensity
IBlack='\033[0;90m' 
IRed='\033[0;91m'   
IGreen='\033[0;92m' 
IYellow='\033[0;93m'
IBlue='\033[0;94m'  
IPurple='\033[0;95m'
ICyan='\033[0;96m'  
IWhite='\033[0;97m'

main() {
    if [[ "$1" == "CHOOSE_STACK" ]]; then
        chooseStack $2
    elif [[ "$1" == "CHECK_BOOTSTRAP" ]]; then
        checkBootstrap $2
    elif [[ "$1" == "LIST_DIFFS" ]]; then
        listDiffs
    else
        printf "\n   ${IGreen}Invalid Script choice, valid options: CHOOSE_STACK\n\n"
        printf "${Reset}"
        exit 1
    fi
    printf "${Reset}"
}

listDiffs() {
    echo ""
    printf "${Green} 🚀 List Diffs in Stacks${Reset}\n"
    STACKS=$(cdk list | sed ':a;N;$!ba;s/\n/ /g')
    index=0
    for stack in $STACKS
    do
        index=$(( $index + 1 ))
        diff=" OK "
        cdk diff --fail $stack >/dev/null 2>&1 || diff="${IRed}DIFF"
        printf "   ${Green}[ ${IYellow}$diff${Green} ] ${IBlue}$stack\n"
    done
}

checkBootstrap() {
    local reg=$1
    local cdkToolkitStackName="CDKToolkit"
    local return=""
    # result=$(aws cloudformation list-stacks --region $reg --query "StackSummaries[?StackName=='$cdkToolkitStackName' && (StackStatus=='CREATE_COMPLETE' || StackStatus=='UPDATE_COMPLETE')].StackId" --output text)
    result=$(aws cloudformation list-stacks --region $reg --query "StackSummaries[?StackName=='$cdkToolkitStackName' && StackStatus=='CREATE_COMPLETE'].StackId" --output text)
    if [[ "$result" != "" ]]; then
        return="$result"
    fi
    export RESULT=$return
}

chooseStack() {
    listStacks RESULT TOTAL $1
    printf "${Green}\n   [${IBlue}ENTER${Green}] for ${IYellow}Exit${Green}\n"
    read -p           "   Choose a Stage/Stack [0-$TOTAL]: " resp
    if [ "$resp" = "0" ]; then
        export RESULT=$RESULT
    elif [ "$resp" = "" ]; then
        echo ""
        exit
    elif (( $resp > $TOTAL )); then
        printf "\n   ${IGreen}Invalid choice, ${IRed}$resp${IGreen} > $TOTAL\n\n"
        exit 1
    else
        declare -a array=($RESULT)
        export RESULT="${array[(($resp - 1))]}"
    fi

}

listStacks() {
    echo ""
    printf "${Green} 🚀 List of Stacks for... ${IYellow}$3${Reset}\n"
    local -n LIST_STACKS=$1
    local -n LIST_STACKS_TOTAL=$2
    STACKS=$(cdk list | sed ':a;N;$!ba;s/\n/ /g')
    index=0
    for line in $STACKS
    do
        LIST_STACKS+="$line "
        if [[ $index == 0 ]]; then
            printf "   ${Green}[${IYellow}$index${Green}] ${IGreen}ALL ${IBlue}of them\n"
        fi
        index=$(( $index + 1 ))
        printf "   ${Green}[${IYellow}$index${Green}] ${IBlue}$line\n"
    done
    LIST_STACKS_TOTAL=$index
}


main $1 $2 $3 $4 $5