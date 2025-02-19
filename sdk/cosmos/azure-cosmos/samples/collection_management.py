import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
from azure.cosmos.partition_key import PartitionKey

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure Cosmos account - 
#    https://azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package - 
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Container resource for Azure Cosmos
# 
# 1. Query for Container
#  
# 2. Create Container
#    2.1 - Basic Create
#    2.2 - Create container with custom IndexPolicy
#    2.3 - Create container with offer throughput set
#    2.4 - Create container with unique key
#    2.5 - Create Collection with partition key V2
#    2.6 - Create Collection with partition key V1
#
# 3. Manage Container Offer Throughput
#    3.1 - Get Container performance tier
#    3.2 - Change performance tier
#
# 4. Get a Container by its Id property
#
# 5. List all Container resources in a Database
#
# 6. Delete Container
# ----------------------------------------------------------------------------------------------------------
# Note - 
# 
# Running this sample will create (and delete) multiple Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the performance tier of that account. 
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


def find_container(db, id):
    print('1. Query for Container')

    containers = list(db.query_containers(
        {
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": id }
            ]
        }
    ))

    if len(containers) > 0:
        print('Container with id \'{0}\' was found'.format(id))
    else:
        print('No container with id \'{0}\' was found'. format(id))
    

def create_container(db, id):
    """ Execute the most basic Create of container. 
    This will create a container with 400 RUs throughput and default indexing policy """

    partition_key = PartitionKey(path='/id', kind='Hash')
    print("\n2.1 Create Container - Basic")
    
    try:
        db.create_container(id=id, partition_key=partition_key)
        print('Container with id \'{0}\' created'.format(id))

    except errors.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(id))               

    print("\n2.2 Create Container - With custom index policy")
    
    try:
        coll = {
            "id": "container_custom_index_policy",
            "indexingPolicy": {
                "indexingMode": "lazy",
                "automatic": False
            }
        }

        container = db.create_container(
            id=coll['id'],
            partition_key=partition_key,
            indexing_policy=coll['indexingPolicy']
        )
        properties = container.read()
        print('Container with id \'{0}\' created'.format(container.id))
        print('IndexPolicy Mode - \'{0}\''.format(properties['indexingPolicy']['indexingMode']))
        print('IndexPolicy Automatic - \'{0}\''.format(properties['indexingPolicy']['automatic']))
        
    except errors.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(coll['id']))

    print("\n2.3 Create Container - With custom offer throughput")

    try:
        coll = {"id": "container_custom_throughput"}
        container = db.create_container(
            id=coll['id'],
            partition_key=partition_key,
            offer_throughput=400
        )
        print('Container with id \'{0}\' created'.format(container.id))
        
    except errors.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(coll['id']))

    print("\n2.4 Create Container - With Unique keys")

    try:
        container = db.create_container(
            id="container_unique_keys",
            partition_key=partition_key,
            unique_key_policy={'uniqueKeys': [{'paths': ['/field1/field2', '/field3']}]}
        )
        properties = container.read()
        unique_key_paths = properties['uniqueKeyPolicy']['uniqueKeys'][0]['paths']
        print('Container with id \'{0}\' created'.format(container.id))
        print('Unique Key Paths - \'{0}\', \'{1}\''.format(unique_key_paths[0], unique_key_paths[1]))
        
    except errors.CosmosResourceExistsError:
        print('A container with id \'container_unique_keys\' already exists')

    print("\n2.5 Create Collection - With Partition key V2 (Default)")

    try:
        container = db.create_container(
            id="collection_partition_key_v2",
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        properties = container.read()
        print('Container with id \'{0}\' created'.format(container.id))
        print('Partition Key - \'{0}\''.format(properties['partitionKey']))

    except errors.CosmosResourceExistsError:
        print('A container with id \'collection_partition_key_v2\' already exists')

    print("\n2.6 Create Collection - With Partition key V1")

    try:
        container = db.create_container(
            id="collection_partition_key_v1",
            partition_key=PartitionKey(path='/id', kind='Hash', version=1)
        )
        properties = container.read()
        print('Container with id \'{0}\' created'.format(container.id))
        print('Partition Key - \'{0}\''.format(properties['partitionKey']))

    except errors.CosmosResourceExistsError:
        print('A container with id \'collection_partition_key_v1\' already exists')


def manage_offer_throughput(db, id):
    print("\n3.1 Get Container Performance tier")
    
    #A Container's Offer Throughput determines the performance throughput of a container. 
    #A Container is loosely coupled to Offer through the Offer's offerResourceId
    #Offer.offerResourceId == Container._rid
    #Offer.resource == Container._self
    
    try:
        # read the container, so we can get its _self
        container = db.get_container_client(container=id)

        # now use its _self to query for Offers
        offer = container.read_offer()
        
        print('Found Offer \'{0}\' for Container \'{1}\' and its throughput is \'{2}\''.format(offer.properties['id'], container.id, offer.properties['content']['offerThroughput']))

    except errors.CosmosResourceExistsError:
        print('A container with id \'{0}\' does not exist'.format(id))

    print("\n3.2 Change Offer Throughput of Container")
                        
    #The Offer Throughput of a container controls the throughput allocated to the Container

    #The following code shows how you can change Container's throughput
    offer = container.replace_throughput(offer.offer_throughput + 100)
    print('Replaced Offer. Offer Throughput is now \'{0}\''.format(offer.properties['content']['offerThroughput']))
                            

def read_Container(db, id):
    print("\n4. Get a Container by id")

    try:
        container = db.get_container_client(id)
        print('Container with id \'{0}\' was found, it\'s link is {1}'.format(container.id, container.container_link))

    except errors.CosmosResourceNotFoundError:
        print('A container with id \'{0}\' does not exist'.format(id))   


def list_Containers(db):
    print("\n5. List all Container in a Database")
    
    print('Containers:')
    
    containers = list(db.list_containers())
    
    if not containers:
        return

    for container in containers:
        print(container['id'])
    

def delete_Container(db, id):
    print("\n6. Delete Container")
    
    try:
        db.delete_container(id)

        print('Container with id \'{0}\' was deleted'.format(id))

    except errors.CosmosResourceNotFoundError:
        print('A container with id \'{0}\' does not exist'.format(id))


def run_sample():

    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )
    try:
        # setup database for this sample
        try:
            db = client.create_database(id=DATABASE_ID)
        
        except errors.CosmosResourceExistsError:
            db = client.get_database_client(DATABASE_ID)
        
        # query for a container            
        find_container(db, CONTAINER_ID)
        
        # create a container
        create_container(db, CONTAINER_ID)
        
        # get & change Offer Throughput of container
        manage_offer_throughput(db, CONTAINER_ID)

        # get a container using its id
        read_Container(db, CONTAINER_ID)

        # list all container on an account
        list_Containers(db)

        # delete container by id
        delete_Container(db, CONTAINER_ID)

        # cleanup database after sample
        try:
            client.delete_database(db)
        
        except errors.CosmosResourceNotFoundError:
            pass

    except errors.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))
    
    finally:
            print("\nrun_sample done")


if __name__ == '__main__':
    run_sample()

