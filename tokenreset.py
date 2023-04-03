from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def token(rollno,seconds):
    s=Serializer('*feojf68958#',seconds)
    return s.dumps({'user':rollno}).decode('utf-8')
