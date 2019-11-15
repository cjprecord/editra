#!/bin/bash

# Build Script for automating the building of all the plugin projects into
# Python Eggs.

# Variables
CWD=$(pwd)
EXPATH=$(dirname $0)
VERBOSE=0

# Make output pretty
BLUE="[34;01m"
CYAN="[36;01m"
GREEN="[32;01m"
RED="[31;01m"
YELLOW="[33;01m"
OFF="[0m"

### Helper Functions ###

###############################################################################
# print_help
# Print help message of available commands
###############################################################################
print_help () {
    echo "Editra Plugins Build Script"
    echo "Type 'build_all.sh [hv]' to run a build command"
    echo ""
    echo "Available Options:"
    echo "  -h      Print This help message"
    echo "  -v      Verbose build information"
    echo "  -c      Clean all temporary build files"
    echo ""
}

###############################################################################
# clean_all
# Do a clean of all build files
###############################################################################
clean_all () {
    shopt -s extglob
    DELCMD="rm -rf"

    # Clean all built plugins from this directory
    echo "${CYAN}Starting Clean${OFF}"
    echo "${GREEN}Cleaning${OFF} toplevel directory"
    for plugin in $(ls); do
        if ! [ -z `echo $plugin | grep '.*\.egg\|pyc\|pyo\|~'` ]; then
            echo "${RED}  rm${OFF} $plugin"
            rm $plugin
        fi
    done

    # Clean all subdirectories
    for plugin in $(ls); do
        if [ -d "$plugin" ]; then
            echo "${GREEN}Cleaning${OFF} $plugin...";
            cd $plugin
            for dir in $(ls); do
                RES=`echo $dir | grep 'dist\|build\|.*\.egg-info\|~'`
                if ! [ -z "$RES" ]; then
                    echo "  ${RED}${DELCMD}${OFF} $plugin/$dir"
                    `$DELCMD $dir`
                fi
            done
            cd ..
        fi
    done
}

###############################################################################
# build_all
# Build all plugins using the setup.py files found in the sub
# directories of this directory. All dist (egg) files are placed
# in this directory.
###############################################################################
build_all () {
    # Commands
    if [ $VERBOSE -ne 0 ]; then
        BUILD="setup.py bdist_egg --dist-dir=../."
    else
        BUILD="setup.py --quiet bdist_egg --dist-dir=../."
    fi

    ## Check what Pythons are available (2.5, 2.6, 2.7) ##
    python2.7 -V 2>/dev/null
    if [ $? -eq 0 ]; then
       PY27="python2.7"
    fi

    python2.6 -V 2>/dev/null
    if [ $? -eq 0 ]; then
       PY26="python2.6"
    fi

    python2.5 -V 2>/dev/null
    if [ $? -eq 0 ]; then
       PY25="python2.5"
    fi

    # Abort if no suitable python is found
    if [[ -z "$PY27" && -z "$PY26" && -z "$PY25" ]]; then
        echo "${RED}!!${OFF} Neither Python 2.4 or 2.5 could be found ${RED}!!${OFF}"
        echo "${RED}!!${OFF} Aborting build ${RED}!!${OFF}"
        exit
    fi

    #### Do the Builds ####
    echo ""
    echo "${YELLOW}**${OFF} Enumerating all plugins... ${YELLOW}**${OFF} "
    echo ""

    for plugin in $(ls); do
        if [ -d "$plugin" ]; then
            echo "${GREEN}Building${OFF} $plugin...";
            cd $plugin

            if [ -n "$PY27" ]; then
                echo "${CYAN}Python2.7${OFF} Building..";
                `$PY27 $BUILD`
                echo "${CYAN}Python2.7${OFF} Build finished"
            fi

            if [ -n "$PY26" ]; then
                echo "${CYAN}Python2.6${OFF} Building..";
                `$PY26 $BUILD`
                echo "${CYAN}Python2.6${OFF} Build finished"
            fi

            if [ -n "$PY25" ]; then
                echo "${CYAN}Python2.5${OFF} Building..";
                `$PY25 $BUILD`
                echo "${CYAN}Python2.5${OFF} Build finished"
            fi

            cd ..
            echo ""
        fi
    done

    echo ""
    echo "${YELLOW}**${OFF} Finished Building all plugins ${YELLOW}**${OFF}"
    echo ""

}

# Parse command line args and set associated params
while getopts "hvc" flag
do
    if [[ "$flag" == "h" ]]; then
        print_help
        exit
    elif [[ "$flag" == "v" ]]; then
        VERBOSE=1
    elif [[ "$flag" == "c" ]]; then
        clean_all
        exit
    else
        continue
    fi
done

# Do the build if no other command have been specified
build_all
