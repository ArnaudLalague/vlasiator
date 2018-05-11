import numpy as np
import pdb

def findParent(id, gridSize, debug):

    nIndicesInRefLvl = list()
    for refLvl in np.arange(1,10):
        nIndicesInRefLvl.append(gridSize * 2 ** ((refLvl - 1) * 3))
    
    for i,_ in enumerate(nIndicesInRefLvl):
        if id <= sum(nIndicesInRefLvl[:i+1]):
            refLvl = i
            break
    if refLvl == 0:
        if id > 0:
            #print("cell {:3d}".format(id)+" is not refined")
            pass
            
        return 0, refLvl       
    
    id2 = id - sum(nIndicesInRefLvl[:refLvl])
    ix = (id2 - 1) % (xdim * 2 ** refLvl) + 1
    iy = (id2 - 1) / (xdim * 2 ** refLvl) % (ydim * 2 ** refLvl) + 1
    iz = (id2 - 1) / (xdim * 2 ** refLvl * ydim * 2 ** refLvl) + 1
    parentId = (int(np.ceil(iz / 2.0) - 1) * xdim * 2 ** (refLvl - 1) * ydim * 2 ** (refLvl - 1) +
                int(np.ceil(iy / 2.0) - 1) * xdim * 2 ** (refLvl - 1) +
                int(np.ceil(ix / 2.0)) +
                sum(nIndicesInRefLvl[:refLvl-1]))
    if debug:
        print("id = {:3d}".format(id)+", id2 = {:3d}".format(id2)+
              ", col = {:2d}".format(ix)+", row = {:2d}".format(iy)+
              ", plane = {:2d}".format(iz)+", parentId = {:2d}".format(parentId)+
              ", refLvl = {:1d}".format(refLvl))
    else:
        #print("cell {:3d}".format(id)+" is the child of cell {:2d}".format(parentId))
        pass

    return parentId, refLvl

def getChildren(children, parentIds, up = True, left = True):

    down  = not up
    right = not left
        
    N = 8

    myChildren = list()
    for id in parentIds:
    
        if up and left:
            i1 = 0
            i2 = 1
        if down and left:
            i1 = 2
            i2 = 3
        if up and right:
            i1 = 4
            i2 = 5
        if down and right:
            i1 = 6
            i2 = 7

        if id in children.keys():
            myChildren.extend(children[id][i1::N])
            myChildren.extend(children[id][i2::N])
        else:
            # If no children were found, return the parent
            myChildren.append(id)
            
    return myChildren


debug = False

filename = "grid_test.out"
fh = open(filename)
lines = fh.readlines()
fh.close()

ids = list()

for i,line in enumerate(lines):
    #print(line[:-1])
    words = line.split()
    if i == 0:
        xdim = int(words[6])
        ydim = int(words[8])
        zdim = int(words[10])
    else:
        ids.append(int(words[3]))

gridSize = xdim*ydim*zdim

#debug = True

parents = dict()
children = dict()
refLvls = dict()
hasChildren = list()

for id in ids:

    # Find the parent of cell id
    parentId, refLvl = findParent(id,gridSize,debug)
    
    parents[id] = parentId
    refLvls[id] = refLvl

    # Parents are not stored in the id array by default, let's add them
    # For completeness
    if not parentId in ids and parentId > 0:
        ids.append(parentId)

    # Make a list of cells that have been refined at least once
    if parentId > 0:
        if not parentId in hasChildren:
            children[parentId] = list()
            hasChildren.append(parentId)

        # Make a list of children for each cell        
        children[parentId].append(id)

for key in children.keys():
    children[key].sort()
ids.sort()

# Second pass to count how many times each cell has been refined
isRefined = dict()
for id in ids:
    isRefined[id] = 0
    if refLvls[id] > 0:
        parentId = parents[id]
        while parentId is not 0:
            isRefined[parentId] = refLvls[id] - refLvls[parentId]
            parentId = parents[parentId]

# Begin sorting, select the dimension by which we sort
dimension = 0

# Sort the mesh ids using Sebastians c++ code
if dimension == 0:

    pass

if dimension == 1:

    pass

if dimension == 2:

    pass

# Create a list of unrefined cells
sortedUnrefinedIds = dict()
for id in isRefined.keys():
    if refLvls[id] == 0:
        sortedUnrefinedIds[id] = isRefined[id]

# Create pencils of unrefined cells, store the level of refinement for each cell
unrefinedPencils = list()
for iz in np.arange(zdim):
    for iy in np.arange(ydim):
        ibeg = iz * zdim + iy * ydim
        iend = iz * zdim + (iy + 1) * ydim
        unrefinedPencils.append({'ids' : sortedUnrefinedIds.keys()[ibeg:iend],
                                 'refLvl' : sortedUnrefinedIds.values()[ibeg:iend]})

# Refine the unrefined pencils that contain refined cells
#print
#print('*** Refining ***')
#print

pencils = list()
parentIds = list()
up = True
left = True

# Loop over the unrefined pencils
for row,unrefinedPencil in enumerate(unrefinedPencils):
    # Refine each pencil according to its max refinement level, then remove duplicates
    maxRefLvl = max(unrefinedPencil['refLvl'])
    # We are creating pencils along the 'x' axis, loop over the 'y' and 'z' axes
    # Assuming the refinement has been done equally in each dimension
    for i in np.arange(2 ** maxRefLvl):
        for j in np.arange(2 ** maxRefLvl):
            #print('Starting new pencil, row = {:1d}, subrow = {:1d}, column = {:1d}'.format(row,i,j))
            pencilIds = list()
            # Walk along the unrefined pencil
            for ix in np.arange(xdim):
                maxLocalRefLvl = unrefinedPencil['refLvl'][ix]
                #print('  ix = {:1d}, maxLocalRefLvl = {:1d}'.format(ix,maxLocalRefLvl))
                # Walk down the refinement tree of the parent cell
                parentIds.append(unrefinedPencil['ids'][ix])
                #offsets = np.zeros(maxLocalRefLvl, dtype = int)
                offset = 0
                nUnRefined = 0
                iRefined = 0
                for iref in np.arange(max(maxLocalRefLvl,1)):

                    # Logic for selecting cells for the pencil among the child cells
                    left = ( (j / 2 ** (maxRefLvl - iref - 1)) % 2 == 0 )
                    up   = ( (i / 2 ** (maxRefLvl - iref - 1)) % 2 == 0 )

                    #print('    iref = {:1d}, up = {:b}, left = {:b}'.format(iref,up,left))
                    # The function getChildren returns the children of the parent, or the
                    # parent itself if it has no children
                    cells = getChildren(children, parentIds, up, left)
                    #print(cells)
                    parentIds = list()

                    offset = nUnRefined - iRefined
                    for k,icell in enumerate(cells):

                        #print('      icell = {:3d}').format(icell)
                        
                        # Add cells that do not have further refinement to the pencil
                        if isRefined[icell] == 0:
                            # Count the number of unrefined cells that have been added during
                            # this iteration
                            nUnRefined += 1
                            # The offset is the number of unrefined cells from the last
                            # iteration minus the index of the refined cell.
                            if offset > 0:
                                pencilIds.insert(-offset,icell)
                            else:
                                pencilIds.append(icell)
                        else:
                            # Store the index of the refined cell
                            iRefined = k
                            
                            # Add to cells to be processed on the next refinement level
                            parentIds.append(icell)
                            
                parentIds = list()

            # Add to the list of pencils if ids are not a duplicate of the previous
            # pencil. This gets rid of most duplicates, but not all of them. Needs fixing.
            if len(pencils) == 0 or not pencilIds == pencils[-1]['ids']:
                pencils.append({'ids'   : pencilIds,
                                'length': len(pencilIds),
                                'width' : 2.0 ** -max(unrefinedPencil['refLvl']),
                                'row'   : row,
                                'subrow' : i,
                                'subcolumn' : j})
            else:
                pass
                #print('Removing duplicate pencil')

                
    
