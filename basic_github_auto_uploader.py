# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 22:49:00 2020
@author: Drew

____________________________________________________________________

basic_github_auto_uploader.py - A Basic Automated GitHub Uploader
____________________________________________________________________

1. Requirements:
    Version:                                Python 3.7
    Built-in Libs:                          base64, os, shutil, time, datetime
    Dependencies:                           pygithub, Git (maybe)

2. Description:
    This file automatically uploads subdirectories as new repositories in
    GitHub. You will need an internet connection to do this.
    The first function [subdir_maker(directory)] will sort the subdirectories
    in the folder. 
    The second function [daily_github_upload(subdirs)] will do the actual repo 
    creation and commit.
    The second function can be fun on a schedule using a for loop and 
    time.sleep or a dedicated scheduling library. You need to restart the
    script if you add new subdirectories that you want to upload.    

3. Running Instructions:
    Place this file in a root directory where you keep your project
    subdirectories. Keep the file structure in the subdirectories flat (don't
    make subdirectories in the subdirectory) as this is not handled in this 
    simplified script. Also, support for PDFs is a bit sketchy. 
    Be sure to replace the Github key in the second function with your own 
    generated key. You can configure the README.MD file as well to say a 
    custom message. 
    
4. Performance:
    Performance is poor for now. The script needs to run constantly and uses
    quite a bit of memory. A more efficient future version will be made. 
"""

# Import libraries that we need to use.
import os, shutil, base64, time, datetime
from github import Github, InputGitTreeElement

# Function 1:   Given a directory/file path, return all the subdirectories in
#               the given directory in a list of strings. Uses the os library.
#               Individual files should not be left in the directory.
def subdir_maker(directory):
    # Create an empty list to store the resultant subdirectories in.
    subdirs = []
    # Walk through the directory and add items to the empty list we made.
    for i,j,y in os.walk(directory):
        subdirs.append(i)
    # os.walk's first element is the directory itself, so remove it. 
    subdirs.remove(subdirs[0])
    # Return the list of subdirectories. 
    return subdirs

# Function 2:   When invoked with a filepath, upload all the files. 
#               Does not support subdirectories within the subdirectory. 
#                Also, cannot be empty!
def daily_github_upload(sub_to_repo):
    # Create a Github object that we can use to connect to Github and do work.
    # It must be initialized with a 40-character secret key. You generate this
    # on Github itself. 
    g = Github('****************************************')
    # Copy the location to a local variable. 
    current_subdir = sub_to_repo
    # Extract the subdirectory name - this will be the Repo name. 
    title = current_subdir[current_subdir.rindex("\\")+1:]
    # Create Repo through Github object. We will not work on the repo object.
    repo = g.get_user().create_repo(title)
    # Initialize with a README.MD file. You can configure this as needed. 
    repo.create_file("README.MD","A readme file","This was an auto-upload on "
                     + str(datetime.datetime.now()))
    # The message we will add under the commit. 
    commit_message = "This was automatically committed."
    # Create a list of file objects.
    file_list = []
    # Create a list of file names.
    file_names = []
    # Do a walk through the subdirectory. 
    for subdir, dirs, files in os.walk(current_subdir):
        # For the files in the subdirectory, print them and then add them to
        # list we created, along with the name to the other list. 
        for file in files:
            print(os.path.join(subdir, file))
            file_list.append(os.path.join(subdir, file))
            file_names.append(file)
    # Get the branch to add to. 
    master_ref = repo.get_git_ref('heads/master')
    master_sha = master_ref.object.sha
    base_tree = repo.get_git_tree(master_sha)
    # Create an empty list to add files to. 
    element_list = list()
    # For each file in list of file objects, read and adjust as needed.
    for i, entry in enumerate(file_list):
        # If normal file type.
        with open(entry) as input_file:
            data = input_file.read()
        # If proprietary file type, encode it. 
        if entry.endswith('.png' or '.pdf' or '.xlsx'):
            data = base64.b64encode(data)
        # Put each file that was encoded from above into an appropriate format 
        # to add to a branch.
        element = InputGitTreeElement(file_names[i], '100644', 'blob', data)
        # Append the object created above to the list made before the loop. 
        element_list.append(element)
    # Create a tree with the elements and specify settings to add the element
    # list to the repo. 
    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    # Commit!
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)
    # Remove the subdirectory from the folder so we don't repeat. 
    shutil.rmtree(current_subdir)

def main():
    # Invoke the subdir_maker() function with the current directory at runtime. 
    subs = subdir_maker(os.path.dirname(os.path.realpath(__file__)))
    # Use a loop to call the daily_github_upload() function for each subdir in
    # the subs list. We keep the subs in case we want to see what was uploaded. 
    for i in range(len(subs)):
        # Call the function for each elem of the list. 
        daily_github_upload(subs[i])
        # Print what was done. 
        print("_"*40 + "\n\n" + "Uploaded {0} to Github. ".format(i) + "\n" + "_"*40)
        # Sleep for 24 hours then do it again. 
        time.sleep(86400)
        
