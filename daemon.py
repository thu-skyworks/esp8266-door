import paho.mqtt.client as mqtt
import ldap
import traceback
from peewee import *
from db_models import *
import config

class AuthStatus:
    SUCCESS       = 0
    LDAP_ERR      = -1
    NO_LDAP_ENTRY = -2
    NO_SUCH_USER  = -3
    ACCESS_DEINED = -4
    USER_DISABLED = -5
    EXCEPTION     = -1000

ADS_UF_ACCOUNTDISABLE=2 #https://docs.microsoft.com/en-us/windows/desktop/adschema/a-useraccountcontrol

client=mqtt.Client()

def verify_with_ldap(studnum):
    passed = False
    status = AuthStatus.LDAP_ERR
    conn = ldap.initialize(config.LDAP_URI)
    conn.protocol_version = 3
    conn.set_option(ldap.OPT_REFERRALS, 0)
    try:
        bind_result = conn.simple_bind_s(config.LDAP_USER, config.LDAP_PASS)
        # print("LDAP: Succesfully authenticated")
        search_results = conn.search_s(
                'DC=ad,DC=thu-skyworks,DC=org',
                ldap.SCOPE_SUBTREE,
                "(&(objectClass=person)(employeeNumber={}))".format(studnum),
            )
        search_results = filter(lambda s: s[0] is not None, search_results)
        cnt = 0;
        for dn,details in search_results:
            # print(details)
            if 'userAccountControl' in details: # MS AD
                print("userAccountControl =",int(details['userAccountControl'][0]))
                if int(details['userAccountControl'][0]) & ADS_UF_ACCOUNTDISABLE:
                    status = AuthStatus.USER_DISABLED
                    break
            cnt += 1
        else:
            if cnt>1:
                print("Warning: more than one user matched {}".format(studnum))
            if cnt>0:
                passed = True
                status = AuthStatus.SUCCESS
            else:
                status = AuthStatus.NO_SUCH_USER
    except ldap.INVALID_CREDENTIALS:
        print("LDAP: Invalid credentials")
    except ldap.SERVER_DOWN:
        print("LDAP: Server down")
    except ldap.LDAPError as e:
        print("LDAP: Other LDAP error: ", e)
    finally:
        conn.unbind_s()
    return passed, status

def log_handle(msg):
    print("[client]" + str(msg.payload))

def verify_card(msg):
    card_number = '{:010d}'.format(int(msg.payload))
    status = AuthStatus.EXCEPTION
    try:
        one = AccountInfo.select().where(AccountInfo.cardnum == card_number).get()

        print("Access Request by", one.studnum, one.realname)
        assert len(one.studnum) > 0 and int(one.studnum) > 0

        success, status = verify_with_ldap(one.studnum)
        if success:
            client.publish("/command", "open")
            print("Valid card, opening the door")
        else:
            print("Invalid card:", card_number)
        AccessRecords.create(
            realname = one.realname,
            studnum  = one.studnum,
            cardnum  = one.cardnum,
            status   = status,
            ).save()

    except AccountInfo.DoesNotExist:
        print("No Records Found for {}".format(msg.payload))
        AccessRecords.create(
            cardnum  = card_number,
            status   = AuthStatus.NO_SUCH_USER,
            ).save()
    except Exception as e:

        AccessRecords.create(
            cardnum  = card_number,
            status   = AuthStatus.EXCEPTION,
            ).save()

        raise e


topics = {"/log": log_handle, "/rs485": log_handle, "/cardverify": verify_card}

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe("/cardverify")
    client.subscribe("/rs485")
    client.subscribe("/log")

def on_message(client, userdata, msg):
    # print("Received message " + str(msg.payload) + " from topic " + msg.topic)
    try:
        topics.get(msg.topic)(msg)
    except Exception as e:
        traceback.print_exc()

DB_Init()

client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set(config.MQTT_USER, config.MQTT_PASSWORD)
client.connect(config.MQTT_BROKER, 1883)

client.loop_forever()
