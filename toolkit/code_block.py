# centerPivotBottom.py

import maya.cmds as cmds

selectionList = cmds.ls(orderedSelection=True)

if len(selectionList) == 1:
    targetName = selectionList[0]

    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

    # Find lowest Y vertex
    bbox = cmds.xform(targetName, q=True, bb=True)

    centerX = (bbox[0] + bbox[3]) / 2
    bottomY = bbox[1]
    centerZ = (bbox[2] + bbox[5]) / 2

    cmds.move(centerX, bottomY, centerZ, targetName + '.rotatePivot')
    cmds.move(centerX, bottomY, centerZ, targetName + '.scalePivot')
else:
    print 'You must select One Item!'


# Makes sure all names are unique in a scene.
# Made by and Copyright Max Boughen www.maxtextures.com
# Please drop me a mail if you wish to modify.


def deletUniqueNames():

    allObjects = cmds.ls(fl=True)

    # Identify the objects that are not unique.
    objectsWithExtra = []
    for object in allObjects:
        try:
            objectInSel = object.split('|')
            if objectInSel[1] not in objectsWithExtra:
                objectsWithExtra.append(objectInSel[1])
        except:
            pass

    # Attempt to get maya to rename the objects and see it do its work.
    counter = 0
    for object in allObjects:
        try:
            objectInSel = object.split('|')
            if objectInSel[1] in objectsWithExtra:
                counter = counter+1
                cmds.rename(object, object)
        except:
            pass

    if counter > 0:
        cmds.warning('There were '+str(counter) +
                     ' objects (including shape nodes) renamed to incorperate their perants name. We will check again..')
        deletUniqueNames()
    else:
        cmds.warning('There were no objects renamed to incorperate their perants name...')


deletUniqueNames()
