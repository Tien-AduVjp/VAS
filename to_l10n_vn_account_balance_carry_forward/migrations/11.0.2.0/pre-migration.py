
def migrate(env, version):
    xml_ids = (
        'account_balance_carry_forward_rule_521',
        'account_balance_carry_forward_rule_511',
        'account_balance_carry_forward_rule_711',
        'account_balance_carry_forward_rule_61xx',
        'account_balance_carry_forward_rule_62xx',
        'account_balance_carry_forward_rule_63xx',
        'account_balance_carry_forward_rule_64xx',
        'account_balance_carry_forward_rule_811',
        'account_balance_carry_forward_rule_821',
        'account_balance_carry_forward_rule_profit_loss'
        )
    env.execute("""
        select res_id from ir_model_data where model='balance.carry.forward.rule' and name in %s;
        """, (xml_ids,))
    res = env.fetchall()
    ids = []
    for tup in res:
        ids.append(tup[0])

    env.execute("""
        UPDATE balance_carry_forward_rule SET forward_type = 'auto' where forward_type != 'auto' and id in %s;
    """, (tuple(ids),))

