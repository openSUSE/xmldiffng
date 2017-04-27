from xmldiff import fmes
from xmldiff.fmes import FmesCorrector

class FmesCorrectorRNG(FmesCorrector):
    def __init__(self, formatter, rngdict=None, f=0.6, t=0.5): # f=0,59
        rngjson = '/suse/fweiss/Documents/werkstudent/bachelorarbeit/xmldiffng/contrib/rng.json'
        self.rngdict = json.load(open(rngjson, 'r'))

        for key in self.rngdict:
            value = self.rngdict[key]
            if value is None:
                self.rngdict[key] = dict()
            else:
                self.rngdict[key] = dict(value)

        # algorithm parameters
        if f>1 or f<0 or t>1 or t<0.5:
            raise Exception('Invalid parameters:  1 > f > 0 and 1 > t > 0.5')
        self.F = f
        self.T = t
        self._formatter = formatter

    def process_trees(self, tree1, tree2):
        """
        Process the two trees
        """
        # add needed attribute (INORDER)
        _init_tree(tree1, map_attr=1)
        _init_tree(tree2)
	#print '**** TREE 2'
        #print node_repr(tree2)
        #print '**** TREE 1'
        #print node_repr(tree1)
        # attributes initialisation
        self._mapping = []  # empty mapping
        self.add_action = self._formatter.add_action
        self._d1, self._d2 = {}, {}
        # give references to the C extensions specific to fmes
        fmes_init(self._mapping, self._d1, self._d2, self.T)
        self._dict = {}
        self._tmp_attrs_dict = {}
        self._pending = []
        self._formatter.init()
        # step 0: mapping
        self._fast_match(tree1, tree2)
        # free matching variables
        match_end()
        del self._d1
        del self._d2
        # step 1: breadth first search tree2
        self._fmes_step1(tree2, tree1)
        # step 2: post order traversal tree1
        self._fmes_step2(tree1, tree2)
        # step 3: rename tmp attributes
        for tmp_name, real_name in self._tmp_attrs_dict.items():
            self.add_action(['rename','//%s'%tmp_name, real_name])
        # free mapping ref in C extensions
        fmes_end()
        self._formatter.end()


    def _fmes_step1(self, tree2, tree1):
        """ first step of the edit script algorithm
        combines the update, insert, align and move phases
        """
        mapping = self._mapping
        fp = self._find_pos
        al = self._align_children
        _partner = partner
        # x the current node in the breadth-first order traversal
        for x in make_bfo_list(tree2):
            y = x[N_PARENT]
            z = _partner(1, y)
            w = _partner(1, x)
            # insert
            if not w:
                todo = 1
                # avoid to add existing attribute node
                if x[N_TYPE] == NT_ATTN:
                    for w in z[N_CHILDS]:
                        if w[N_TYPE] != NT_ATTN:
                            break
                        elif w[N_VALUE] == x[N_VALUE]:
                            ## FIXME: what if w or w[N_CHILDS][0] yet mapped ??
                            if not w[N_MAPPED]:
##                                 old_value = x[N_VALUE]
##                                 x[N_VALUE] = 'xmldiff-%s'%old_value
##                                 self._tmp_attrs_dict[x[N_VALUE]] = old_value
##                                 old_x = _partner(0, w)
##                                 i = 0
##                                 for i in range(len(mapping)):
##                                     if mapping[i][0] is w:
##                                         print mapping[i][1]
##                                         mapping[i][1][N_MAPPED] = FALSE
##                                         mapping.pop(i)
##                                         break
##                             else:
                                todo = None
                                w[N_MAPPED] = TRUE
                                mapping.append((w, x))
                                # print 'delete 1'
                                # if not w[N_CHILDS][0]:
                                delete_node(w[N_CHILDS][0])
                            break

                    #-----------------------
                if todo is not None:
                    x[N_INORDER] = TRUE
                    k = fp(x)
                    # w = copy(x)
                    w = x[:]
                    w[N_CHILDS] = []
                    w.append(TRUE) # <-> w[N_MAPPED] = TRUE
                    mapping.append((w, x))
                    # avoid coalescing two text nodes
                    if w[N_TYPE] == NT_TEXT:
                        k = self._before_insert_text(z, w, k)
                    # real insert on tree 1
                    insert_node(z, w, k)
                    # make actions on subtree
                    self._dict[id(w)] = ww = w[:]
                    ww[N_CHILDS] = []
                    # preformat action
                    if not self._dict.has_key(id(z)):
                        #print "Knoten x ist: %s" % x[N_TYPE]
                        #print "Knoten w ist %s" % w[N_TYPE]
                        if w[N_TYPE] == NT_ATTV:
                            action = ['update', f_xpath(z), w[N_VALUE]]
                            self.add_action(action)
                        # node is attribute node
                        elif w[N_TYPE] == NT_ATTN:
                            #print "%s is attribute node => check if it is in the dictionary..." % w[N_VALUE]
                            if self._searchkey(w[N_VALUE]):
                                #print "   yes, -%s- is in the dictionary" % w[NT_ATTN]
                                #print "      Value in dictionary: %s" % self._getvalue(w[N_VALUE])
                                #print "      Value in node: %s" % x[N_CHILDS][0][2]
                                if self._getvalue(w[N_VALUE]) != x[N_CHILDS][0][2]:
                                    # values are different => insert the node
                                    print "x != default"
                                    action = ['append BLA', f_xpath(z), ww]
                                    self.add_action(action)

                                else:
                                    # do not insert the node
                                    print "-----Values are identical => skip insert-----\n"
                            else:
                                print "insert/append attribute %s" % w[N_VALUE]
                                #print "value of attribute: %s" % self._getvalue(w[N_VALUE])
                                action = ['append BLA', f_xpath(z), ww]
                                self.add_action(action)
                        elif z[N_TYPE] == NT_ROOT:
                            action = ['append-first', '/', ww]
                            self.add_action(action)
                        else:
                            k = get_pos(w)
                            if k <= nb_attrs(z):
                                action = ['append-first',
                                          f_xpath(z), ww]
                                self.add_action(action)
                            else:
                                action = ['insert-after',
                                          f_xpath(z[N_CHILDS][k-1]), ww]
                                self.add_action(action)
                        #self.add_action(action)
                    else:
                        insert_node(self._dict[id(z)], ww, k)
                    #-----------------------
            elif x[N_NAME] != '/':
                v = w[N_PARENT]
                # update
                if w[N_VALUE] != x[N_VALUE]:
                    # format action
                    if w[N_TYPE] == NT_NODE:
                        self.add_action(['rename', f_xpath(w), x[N_VALUE]])
                    elif w[N_TYPE] == NT_ATTN:
                        attr_name = self._before_attribute(w[N_PARENT], w,
                                                           x[N_VALUE])
                        self.add_action(['rename', f_xpath(w), attr_name])
                        x[N_NAME] = '@%sName' % attr_name
                        x[N_VALUE] = attr_name
                    else:
                        self.add_action(['update', f_xpath(w), x[N_VALUE]])
                    # real update on t1
                    w[N_VALUE] = x[N_VALUE]
                    # this is necessary for xpath
                    rename_node(w, x[N_NAME])
                # move x if parents not mapped together
                if not has_couple(v, y):
                    x[N_INORDER] = TRUE
                    k = fp(x)
                    self._make_move(w, z, k)
            # align children
            al(w, x)
#            print 'after', node_repr(tree1)

    def _fmes_step2(self, tree1, tree2):
        """ the delete_node phase of the edit script algorithm

        instead of the standard algorithm, walk on tree1 in pre order and
        add a remove action on node not marked as mapped.
        Avoiding recursion on these node allow to extract remove on subtree
        instead of leaf

        do not use next_sibling for performance issue
        """

        #print "\ndictionary:"
        #print self.rngdict
        #print "keys im dictionary: %s" % self.rngdict.keys()
        #print "-----\n\n"
        stack = []
        i = 0
        node = tree1
        while node is not None:
            if node[N_MAPPED] != TRUE:
                if node[N_PARENT] and len(node[N_PARENT][N_CHILDS]) > i+1:
                    next_node = node[N_PARENT][N_CHILDS][i+1]
                    # if next node is a text node to remove, switch actions
                    if next_node[N_TYPE] == NT_TEXT and \
                       next_node[N_MAPPED] != TRUE:
                        self.add_action(['remove', f_xpath(next_node)])
                        delete_node(next_node)
                        try:
                            next_node = node[N_PARENT][N_CHILDS][i+1]
                        except:
                            next_node = None
                else:
                    next_node = None
                # check if node is attribute node
                #print "Knoten ist %s" % node[N_TYPE]
                #print "if Knoten ist Attribut:"
                if node[N_TYPE] == NT_ATTN:
                    #print "   attribute value: %s" % node[N_VALUE]
                    #print "   check if attribute - %s - is in the dictionary" % node[NT_ATTN]
                    #print "   search key..."
                    if self._searchkey(node[N_VALUE]):
                        #print "      yes, %s is in the dictionary" % node[NT_ATTN]
                        #print "      check if its value is the same as in the dictionary"
                        #print "         Value in dictionary: %s" % self._getvalue(node[N_VALUE])
                        #print "         Value in node: %s" % node[N_CHILDS][0][2]
                        # check if attribute node has the same value as in the dictionary (defaultValue)
                        if self._getvalue(node[N_VALUE]) == node[N_CHILDS][0][2]:
                            # do not delete the node
                            print "-----Values are identical => skip delete-----\n"
                            #print "#### next: %s" %next_node
                            # delete node in order to get the correct next node (if one node has
                            # two attributes and one gets deleted, the next node will be itself again...)
                            delete_node(node)
                            node = next_node
                        else:
                            # delete the node
                            self.add_action(['remove', f_xpath(node)])
                            delete_node(node)
                            node = next_node
                    else:
                        # delete the node
                        self.add_action(['remove', f_xpath(node)])
                        delete_node(node)
                        node = next_node
                else:
                    print "perform delete operation on node %s" % node[NT_ATTN]
                    self.add_action(['remove', f_xpath(node)])
                    delete_node(node)
                    node = next_node
            elif node[N_CHILDS]:
                # push next sibbling on the stack
                if node[N_PARENT] and len(node[N_PARENT][N_CHILDS]) > i+1 :
                    stack.append((node[N_PARENT][N_CHILDS][i+1], i+1))
                node = node[N_CHILDS][0]
                i = 0
            elif node[N_PARENT] and len(node[N_PARENT][N_CHILDS]) > i+1:
                i += 1
                node = node[N_PARENT][N_CHILDS][i] #next_sibling(node)
            else:
                node = None
            if node is None and stack:
                node, i = stack.pop()


    def _searchkey(self, rngkey):
        """
        search for a key in a dictionary
        :param rngkey: key to search for
        :return: True or False
        """
        #return any([rngkey in value.keys() for _, value in self.rngdict.iteritems()])
        return any([rngkey in value for _, value in self.rngdict.iteritems()])


    def _getvalue(self, rngkey):
        """
        get the value of a key in a dictionary
        key kann mehrmals in dictionary vorkommen, aber value ist eindeutig
        :param rngkey: key of the value
        :return: value of the key
        """
        result = []
        for key, value in self.rngdict.iteritems():
            result = value.get(rngkey)
            if result is not None:
                return result
        raise KeyError(rngkey)


