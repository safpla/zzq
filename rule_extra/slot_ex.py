# coding:utf-8
# __author__ = 'yhk'

from __future__ import print_function

import os
import sys
import codecs
import re
import ydir
print(sys.getdefaultencoding())
reload(sys)
sys.setdefaultencoding('utf-8')
print(sys.getdefaultencoding())

# accuser 原告
# defendant 被告
# court 法院
# accuser_claim 原告诉求    1
# defendant_argue 被告辩称  2
# facts 事实认定            3
# court_said 法院认为       4
# court_decision 法院判决   5

re_accuser_name=re.compile(u"原告(.+?)[, . ， 。 ].+")
re_defendant_name=re.compile(u"被告(.+?)[, . ， 。 ].+")
re_accuser_claim=re.compile(u"起诉称[: , ： ，]|^原告.+?诉称[: , ： ，]")
re_defendant_argue=re.compile(u"答辩称[: , ： ，]|被告.+?辩称[: , ： ，]")
re_facts=re.compile(u"经审理查明[: , ： ，]|证明其主张提供了下列证据")
re_court_said=re.compile(u"[本 法]院认为[: , ： ，]")
re_court_decision=re.compile(u"判决如下[: , ： ，]")
re_end=re.compile(u"如不服本判决")

def match_score(re_rule, re_rule_w, line):
    score=0.0
    for idx,re_rule_item in enumerate(re_rule):
        if re_rule_item.findall(line):
            score+=re_rule_w[idx]
    return score

class switch(object):
    def __init__(self, value):
        self.value=value
        self.fail=False
    def __iter__(self):
        """Return the mathch method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fail or not args:
            return True
        elif self.value in args:
            self.fail=True
            return True
        else:
            return False

class Side(object):
    def __init__(self,value):
        self.name=value
        self.paras=[]
    def add_para(self, para):
        self.paras.append(para)
    def write_paras(self,out,prefix=""):
        out.write("%s%s:\n" % (prefix,self.name))
        for line in self.paras:
            out.write("%s%s\n" % (prefix,line))
        out.write("\n")


class Party(object):
    def __init__(self,name,paras):
        self.name=name
        self.party_paras=paras
        self.sentences=[]

    def dividinto_sentence(self):
        for content in self.party_paras:
            lines=re.split(ur'[ ; ； 。]',content)
            empty_n=0
            for idx,line in enumerate(lines):
                line=line.strip()
                if not line:
                    empty_n+=1
                    continue

                if re.match(r'[, ，]',line):
                    self.sentences[idx-1-empty_n]=self.sentences[idx-1-empty_n]+line
                    empty_n+=1
                else:
                    self.sentences.append(line)

class Claim(Side):
    def __init__(self,name,re_rule):
        super(Claim,self).__init__(name)
        self.re_rule=re_rule

    def parse_sentence(self,sentence):
        if self.re_rule.findall(sentence):
            self.add_para(sentence)
            print(sentence)

class ClaimSet(Side):
    def __init__(self,name,re_rule,re_rule_w):
        super(ClaimSet,self).__init__(name)
        self.re_rule=re_rule
        self.re_rule_w=re_rule_w

    def parse_sentence(self,sentence):
        mscore=match_score(self.re_rule,self.re_rule_w,sentence)
        if mscore>0.6:
            self.add_para(sentence)



class AccuserClaim(Party):
    def __init__(self,name,paras):
        super(AccuserClaim,self).__init__(name,paras)
        # 原告诉求-事实依据-综述
        re_accuserclaim_facts=re.compile(u'^[判 令]享有.+?著作权| [^判 令]享有.+?权|侵犯.+?著作权|获得.+?收益|构成.*?不正当竞争行为|造成.*?经济损失|被告未经.*?授权|未经.*?许可')
        self.accuser_facts=Claim("事实依据",re_accuserclaim_facts)
        # 原告诉求-事实依据
        re_accuser_facts_posses=re.compile(u'[^判 令]享有.+?权')
        self.accuser_facts_posses=Claim("享有作品著作权",re_accuser_facts_posses)
        re_accuser_facts_tort=re.compile(u'侵犯.+?著作权')
        self.accuser_facts_tort=Claim("侵犯著作权",re_accuser_facts_tort)
        re_accuser_facts_competition=re.compile(u'构成.*?不正当竞争行为')
        self.accuser_facts_competition=Claim("不正当竞争行为",re_accuser_facts_competition)
        re_accuser_facts_benefit=re.compile(u'获得.+?收益')
        self.accuser_facts_benefit=Claim("是否非法盈利",re_accuser_facts_benefit)
        # 原告诉求-诉讼主张-综述
        re_accuser_zhuzhang=re.compile(u'请求.*?判令.*?行为|被告的行为侵犯了|侵犯.+?著作权|侵犯.+?权')
        self.accuser_zhuzhang=Claim("诉讼主张",re_accuser_zhuzhang)
        # 原告诉求-诉讼主张
        re_accuser_zz_tort_right=re.compile(u'侵犯.+?权')
        self.accuser_zz_tort_right=Claim("侵犯著作权",re_accuser_zz_tort_right)
        re_accuser_zz_unfair_competition=re.compile(u'不正当竞争')
        self.accuser_zz_unfair_competition=Claim("不正当竞争",re_accuser_zz_unfair_competition)
        re_accuser_zz_joint=re.compile(u'连带责任')
        self.accuser_zz_joint=Claim("连带责任",re_accuser_zz_joint)
        # 原告诉求-索赔权益-综述：
        re_accuser_rights=re.compile(u'请求.*?判令|赔偿|故原告要求法院|\d+[、,]')
        self.accuser_rights=Claim("索赔权益",re_accuser_rights)
        # 原告诉求-索赔权益：
        re_accuser_rights_stop_tort=re.compile(u'停止.*?侵权')
        self.accuser_rights_stop_tort=Claim("停止侵权",re_accuser_rights_stop_tort)
        re_accuser_rights_apologize=re.compile(u'赔礼道歉')
        self.accuser_rights_apologize=Claim("赔礼道歉",re_accuser_rights_apologize)
        re_accuser_rights_image=re.compile(u'消除影响')
        self.accuser_rights_image=Claim("消除影响",re_accuser_rights_image)
        re_accuser_rights_loss=re.compile(u'经济损失')
        self.accuser_rights_loss=Claim("经济损失",re_accuser_rights_loss)
        re_accuser_rights_cost=re.compile(u"诉讼费用")
        self.accuser_rights_cost=Claim("诉讼费用",re_accuser_rights_cost)
        re_accuser_rights_revoke_tort=re.compile("撤回")
        self.accuser_rights_revoke_tort=Claim("是否撤回侵权请求",re_accuser_rights_revoke_tort)

    def re_claim_match(self):
        self.dividinto_sentence()
        for sentence in self.sentences:
            # 原告诉求-事实依据--综述
            self.accuser_facts.parse_sentence(sentence)
            # 原告诉求-事实依据
            self.accuser_facts_posses.parse_sentence(sentence)
            self.accuser_facts_tort.parse_sentence(sentence)
            self.accuser_facts_competition.parse_sentence(sentence)
            self.accuser_facts_benefit.parse_sentence(sentence)
            # 原告诉求-诉讼主张-综述
            self.accuser_zhuzhang.parse_sentence(sentence)
            # 原告诉求-诉讼主张
            self.accuser_zz_tort_right.parse_sentence(sentence)
            self.accuser_zz_unfair_competition.parse_sentence(sentence)
            self.accuser_zz_joint.parse_sentence(sentence)
            # 原告诉求-索赔权益-综述
            self.accuser_rights.parse_sentence(sentence)
            # 原告诉求-索赔权益：
            self.accuser_rights_stop_tort.parse_sentence(sentence)
            self.accuser_rights_apologize.parse_sentence(sentence)
            self.accuser_rights_image.parse_sentence(sentence)
            self.accuser_rights_loss.parse_sentence(sentence)
            self.accuser_rights_cost.parse_sentence(sentence)
            self.accuser_rights_revoke_tort.parse_sentence(sentence)

    def write_claim(self,out):
        prefix_l2="\t"
        prefix_l3="\t\t"
        out.write("%s:\n" % (self.name))
        # 原告诉求-事实依据-综述
        self.accuser_facts.write_paras(out,prefix_l2)
        # 原告诉求-事实依据
        self.accuser_facts_posses.write_paras(out,prefix_l3)
        self.accuser_facts_tort.write_paras(out,prefix_l3)
        self.accuser_facts_competition.write_paras(out,prefix_l3)
        self.accuser_facts_benefit.write_paras(out,prefix_l3)
        # 原告诉求-诉讼主张-综述
        self.accuser_zhuzhang.write_paras(out,prefix_l2)
        # 原告诉求-诉讼主张
        self.accuser_zz_tort_right.write_paras(out,prefix_l3)
        self.accuser_zz_unfair_competition.write_paras(out,prefix_l3)
        self.accuser_zz_joint.write_paras(out,prefix_l3)
        # 原告诉求-索赔权益-综述
        self.accuser_rights.write_paras(out,prefix_l2)
        # 索赔权益
        self.accuser_rights_stop_tort.write_paras(out,prefix_l3)
        self.accuser_rights_apologize.write_paras(out,prefix_l3)
        self.accuser_rights_image.write_paras(out,prefix_l3)
        self.accuser_rights_loss.write_paras(out,prefix_l3)
        self.accuser_rights_cost.write_paras(out,prefix_l3)
        self.accuser_rights_revoke_tort.write_paras(out,prefix_l3)

class DefendantArgue(Party):
    def __init__(self,name,paras):
        super(DefendantArgue,self).__init__(name,paras)
        # 被告辩称-是否享有著作权-综述
        re_defendant_right=re.compile(u'证明.*?享有.*?权|不.*?适格|不享有.*?权|无权.*?起诉|效力.*?怀疑')
        self.defendant_right=Claim("是否享有著作权",re_defendant_right)
        # 被告辩称-是否享有著作权
        re_defendant_right_other_person=re.compile(u'其他权利人')
        self.defendant_right_other_person=Claim("是否有其他权利人",re_defendant_right_other_person)
        re_defendant_right_suit_subject=re.compile(u'不.*?适格')
        self.defendant_right_suit_subject=Claim("是否是适格主体",re_defendant_right_suit_subject)
        re_defendant_right_validate=re.compile(u'是否有效')
        self.defendant_right_validate=Claim("著作权是否有效",re_defendant_right_validate)
        # 被告辩称-是否构成侵权行为-综述
        re_defendant_act=re.compile(u'不构成.*?侵权|著作权侵权的角度')
        self.defendant_act=Claim("是否构成侵权行为",re_defendant_act)
        # 被告辩称-是否构成侵权行为
        re_defendant_act_production=re.compile(u'作品是否构成侵权')
        self.defendant_act_production=Claim("作品是否构成侵权",re_defendant_act_production)
        re_defendant_act_apply=re.compile(u'是否适用于著作权')
        self.defendant_act_apply=Claim("是否适用于著作权",re_defendant_act_apply)
        re_defendant_act_evidence=re.compile(u'公证是否可信')
        self.defendant_act_evidence=Claim("公证是否可信",re_defendant_act_evidence)
        # 被告辩称-是否合法提供搜索链接服务-综述
        re_defendant_link=re.compile(u'链接行为|标[识 注].*?来源|搜索链接|内容.*?第三方')
        self.defendant_link=Claim("是否合法提供搜索链接服务",re_defendant_link)
        # 被告辩称-是否合法提供搜索链接服务
        re_defendant_link_third=re.compile(u'内容是否由第三方提供')
        self.defendant_link_third=Claim("内容是否由第三方提供",re_defendant_link_third)
        re_defendant_link_source=re.compile(u'是否注明作品来源')
        self.defendant_link_source=Claim("是否注明作品来源",re_defendant_link_source)
        re_defendant_link_check=re.compile(u'是否对链接内容有审查义务')
        self.defendant_link_check=Claim("是否对链接内容有审查义务",re_defendant_link_check)
        # 被告辩称-是否符合免责条款-综述
        re_defendant_disclaimer=re.compile(u'用户.*?上传|删除.*?视频|已经?停止.*?播放|没有.*?编辑|无法[明 应]知|[没 无]有?.*?获利|合理注意义务|符合.*?免责条款|版权审核|[没 无]有?主观过错|不.*?承担.*?责任|收取.*?费用')
        self.defendant_disclaimer=Claim("是否符合免责条款",re_defendant_disclaimer)
        # 被告辩称-是否符合免责条款
        re_defendant_disclaimer_store=re.compile(u'是否仅提供存储空间')
        self.defendant_disclaimer_store=Claim("是否仅提供存储空间",re_defendant_disclaimer_store)
        re_defendant_disclaimer_edit=re.compile(u'是否改变作品内容')
        self.defendant_disclaimer_edit=Claim("是否改变作品内容",re_defendant_disclaimer_edit)
        re_defendant_disclaimer_check=re.compile(u'是否对作品有审查义务')
        self.defendant_disclaimer_check=Claim("是否对作品有审查义务",re_defendant_disclaimer_check)
        re_defendant_disclaimer_attent_duty=re.compile(u'是否尽到合理注意义务')
        self.defendant_disclaimer_attent_duty=Claim("是否尽到合理注意义务",re_defendant_disclaimer_attent_duty)
        re_defendant_disclaimer_benefit=re.compile(u'是否从作品中直接获利')
        self.defendant_disclaimer_benefit=Claim("是否从作品中直接获利",re_defendant_disclaimer_benefit)
        re_defendant_disclaimer_delete_content=re.compile(u'是否删除侵权内容')
        self.defendant_disclaimer_delete_content=Claim("是否删除侵权内容",re_defendant_disclaimer_delete_content)
        # 被告辩称-是否构成不正当竞争-综述
        re_defendant_competition=re.compile(u'从不正当竞争角度|不存在竞争关系|不构成不正当竞争|实施.*?不正当竞争')
        self.defendant_competitive=Claim("是否构成不正当竞争",re_defendant_disclaimer)
        # 被告辩称-是否构成不正当竞争
        re_defendant_competitive_relation=re.compile(u'是否存在竞争关系')
        self.defendant_competitive_relation=Claim("是否存在竞争关系",re_defendant_competitive_relation)
        re_defendant_competitive_behaviour=re.compile(u'是否符合不正当竞争行为的法律要件')
        self.defendant_competitive_behaviour=Claim("是否符合不正当竞争行为的法律要件",re_defendant_competitive_behaviour)
        # 被告辩称-经济损失是否合理-综述
        re_defendant_loss=re.compile(u'索?赔偿?.*?过高|扩大.*?损失|经济损失|对原告.*?损失|受众.*?小|金额过?高|索赔.*?证据')
        self.defendant_loss=Claim("经济损失是否合理",re_defendant_loss)
        # 被告辩称-经济损失是否合理
        re_defendant_loss_unreasonable=re.compile(u'索?赔偿?.*?过高|经济损失|对原告.*?损失|受众.*?小|金额过?高|索赔.*?证据')
        self.defendant_loss_unreasonable=Claim("费用不合理缺乏依据",re_defendant_loss_unreasonable)
        re_defendant_loss_expand=re.compile(u'扩大.*?损失')
        self.defendant_loss_expand=Claim("原告是否承担扩大损失责任",re_defendant_loss_expand)
        # 是否损害原告形象
        re_defendant_damage_image=re.compile(u'损害.*?形象')
        self.defendant_damage_image=Claim("是否损害原告形象",re_defendant_damage_image)
        # 赔礼道歉缺乏依据
        re_defendant_apologize=re.compile(u'赔礼道歉')
        self.defendant_apologize=Claim("赔礼道歉缺乏依据",re_defendant_apologize)


    def re_claim_match(self):
        self.dividinto_sentence()
        for sentence in self.sentences:
            # 被告辩称-是否享有著作权-综述
            self.defendant_right.parse_sentence(sentence)
            # 被告辩称-原告是否享有著作权
            self.defendant_right_other_person.parse_sentence(sentence)
            self.defendant_right_suit_subject.parse_sentence(sentence)
            self.defendant_right_validate.parse_sentence(sentence)
            # 被告辩称-是否构成侵权行为-综述
            self.defendant_act.parse_sentence(sentence)
            # 被告辩称-是否构成侵权行为
            self.defendant_act_production.parse_sentence(sentence)
            self.defendant_act_apply.parse_sentence(sentence)
            self.defendant_act_evidence.parse_sentence(sentence)
            # 被告辩称-是否合法提供搜索链接服务-综述
            self.defendant_link.parse_sentence(sentence)
            # 被告辩称-是否合法提供搜索链接服务
            self.defendant_link_third.parse_sentence(sentence)
            self.defendant_link_source.parse_sentence(sentence)
            self.defendant_link_check.parse_sentence(sentence)
            # 被告辩称-是否符合免责条款-综述
            self.defendant_disclaimer.parse_sentence(sentence)
            # 被告辩称-是否符合免责条款
            self.defendant_disclaimer_store.parse_sentence(sentence)
            self.defendant_disclaimer_edit.parse_sentence(sentence)
            self.defendant_disclaimer_check.parse_sentence(sentence)
            self.defendant_disclaimer_attent_duty.parse_sentence(sentence)
            self.defendant_disclaimer_benefit.parse_sentence(sentence)
            self.defendant_disclaimer_delete_content.parse_sentence(sentence)
            # 被告辩称-是否构成不正当竞争-综述
            self.defendant_competitive.parse_sentence(sentence)
            # 被告辩称-是否构成不正当竞争
            self.defendant_competitive_relation.parse_sentence(sentence)
            self.defendant_competitive_behaviour.parse_sentence(sentence)
            # 被告辩称-经济损失是否合理-综述
            self.defendant_loss.parse_sentence(sentence)
            # 被告辩称-经济损失是否合理
            self.defendant_loss_unreasonable.parse_sentence(sentence)
            self.defendant_loss_expand.parse_sentence(sentence)
            # 是否损害原告形象
            self.defendant_damage_image.parse_sentence(sentence)
            # 赔礼道歉缺乏依据
            self.defendant_apologize.parse_sentence(sentence)

    def write_claim(self,out):
        prefix_l2="\t"
        prefix_l3="\t\t"
        out.write("%s:\n" % (self.name))
        # 被告辩称-是否享有著作权-综述
        self.defendant_right.write_paras(out,prefix_l2)
        # 原告诉求-诉讼主张
        self.defendant_right_other_person.write_paras(out,prefix_l3)
        self.defendant_right_suit_subject.write_paras(out,prefix_l3)
        self.defendant_right_validate.write_paras(out,prefix_l3)
        # 被告辩称-是否构成侵权行为-综述
        self.defendant_act.write_paras(out,prefix_l2)
        # 被告辩称-是否构成侵权行为
        self.defendant_act_production.write_paras(out,prefix_l3)
        self.defendant_act_apply.write_paras(out,prefix_l3)
        self.defendant_act_evidence.write_paras(out,prefix_l3)
        # 被告辩称-是否合法提供搜索链接服务-综述
        self.defendant_link.write_paras(out,prefix_l2)
        # 被告辩称-是否合法提供搜索链接服务
        self.defendant_link_third.write_paras(out,prefix_l3)
        self.defendant_link_source.write_paras(out,prefix_l3)
        self.defendant_link_check.write_paras(out,prefix_l3)
        # 被告辩称-是否符合免责条款-综述
        self.defendant_disclaimer.write_paras(out,prefix_l2)
        # 被告辩称-是否符合免责条款
        self.defendant_disclaimer_store.write_paras(out,prefix_l3)
        self.defendant_disclaimer_edit.write_paras(out,prefix_l3)
        self.defendant_disclaimer_check.write_paras(out,prefix_l3)
        self.defendant_disclaimer_attent_duty.write_paras(out,prefix_l3)
        self.defendant_disclaimer_benefit.write_paras(out,prefix_l3)
        self.defendant_disclaimer_delete_content.write_paras(out,prefix_l3)
        # 被告辩称-是否构成不正当竞争-综述
        self.defendant_competitive.write_paras(out,prefix_l2)
        # 被告辩称-是否构成不正当竞争
        self.defendant_competitive_relation.write_paras(out,prefix_l3)
        self.defendant_competitive_behaviour.write_paras(out,prefix_l3)
        # 被告辩称-经济损失是否合理-综述
        self.defendant_loss.write_paras(out,prefix_l2)
        # 被告辩称-经济损失是否合理
        self.defendant_loss_unreasonable.write_paras(out,prefix_l3)
        self.defendant_loss_expand.write_paras(out,prefix_l3)
        # 是否损害原告形象
        self.defendant_damage_image.write_paras(out,prefix_l2)
        # 赔礼道歉缺乏依据
        self.defendant_apologize.write_paras(out,prefix_l2)


class Facts(Party):
    def __init__(self,name,paras):
        super(Facts,self).__init__(name,paras)
        # 作品内容认定
        re_facts_production=re.compile(u'《?.+?》片[尾 头].*?署名|播放.*?《.+?》.*?剧集|《.+?》.*?权.*?转让|授权.*?《.+?》|《.+?》.*?电视台|作品类型')
        self.facts_production=Claim("作品内容认定",re_facts_production)

    def re_claim_match(self):
        self.dividinto_sentence()
        for sentence in self.sentences:
            self.facts_production.parse_sentence(sentence)

    def write_claim(self,out):
        prefix_l2="\t"
        prefix_l3="\t\t"
        out.write("%s:\n" % (self.name))
        self.facts_production.write_paras(out,prefix_l2)

class CourtSaid(Party):
    def __init__(self,name,paras):
        super(CourtSaid,self).__init__(name,paras)
        # 作品认定
        re_court_said_production=re.compile(u'《.+?》.*?作为.*?保护')
        self.court_said_production=Claim("作品认定",re_court_said_production)
        # 是否享有著作权
        re_court_said_valid=re.compile(u'可?认[定 为].*?享有.*?权|授权.*?享有.*?权|认定.*?授予.*?原告|对.*?享有.*?权')
        self.court_said_valid=Claim("授权是否有效",re_court_said_valid)
        re_court_said_suit_subject=re.compile(u'诉讼主体是否适格')
        self.court_said_suit_subject=Claim("诉讼主体是否适格",re_court_said_suit_subject)
        # 是否构成直接侵权
        re_court_said_direct_damage=re.compile(u'构成.*?直接的?侵害.*?属?直接侵权')
        self.court_said_direct_damage=Claim("是否构成直接侵权",re_court_said_direct_damage)
        # 是否构成帮助侵权
        re_court_said_help_damage=re.compile(u'故.*?侵.*?权.*?帮助|帮助侵权')
        self.court_said_help_damage=Claim("是否构成帮助侵权",re_court_said_help_damage)
        # 是否符合免责条款
        re_court_said_disclaimer_store=re.compile(u'是否仅提供存储空间')
        self.court_said_disclaimer_store=Claim("是否仅提供存储空间",re_court_said_disclaimer_store)
        re_court_said_disclaimer_edit=re.compile(u'是否改变作品内容')
        self.court_said_disclaimer_edit=Claim("是否改变作品内容",re_court_said_disclaimer_edit)
        re_court_said_disclaimer_check=re.compile(u'是否对作品有审查义务')
        self.court_said_disclaimer_check=Claim("是否对作品有审查义务",re_court_said_disclaimer_check)
        re_court_said_disclaimer_attent_duty=re.compile(u'是否尽到合理注意义务')
        self.court_said_disclaimer_attent_duty=Claim("是否尽到合理注意义务",re_court_said_disclaimer_attent_duty)
        re_court_said_disclaimer_benefit=re.compile(u'是否从作品中直接获利')
        self.court_said_disclaimer_benefit=Claim("是否从作品中直接获利",re_court_said_disclaimer_benefit)
        re_court_said_disclaimer_delete_content=re.compile(u'是否删除侵权内容')
        self.court_said_disclaimer_delete_content=Claim("是否删除侵权内容",re_court_said_disclaimer_delete_content)
        # 搜索链接服务是否合法
        re_court_said_link_spread=re.compile(u'是否构成网络传播')
        self.court_said_link_spread=Claim("是否构成网络传播",re_court_said_link_spread)
        re_court_said_link_access=re.compile(u'是否是合法允许直接访问的链接')
        self.court_said_link_access=Claim("是否是合法允许直接访问的链接",re_court_said_link_access)
        re_court_said_link_complete=re.compile(u'是否实现完整跳转并完全呈现被链接的内容')
        self.court_said_link_complete=Claim("是否实现完整跳转并完全呈现被链接的内容",re_court_said_link_complete)
        re_court_said_link_against_will=re.compile(u'是否违背被链接网站的意愿')
        self.court_said_link_against_will=Claim("是否违背被链接网站的意愿",re_court_said_link_against_will)
        re_court_said_link_random=re.compile(u'全网.*?随机|随机.*?搜索|全网.*?搜索')
        self.court_said_link_random=Claim("是否具有全网随机性",re_court_said_link_random)
        # 是否构成侵权行为
        re_court_said_tort=re.compile(u'公司.*?构成.*?侵权.*?承担.*?责任|综上.*?侵[犯 害].*?权|鉴于.*?应当?承担.*责任|侵犯.*?原告.*?权.*?承担')
        self.court_said_tort=Claim("是否构成侵权行为",re_court_said_tort)

        # 是否构成不正当竞争
        re_court_said_tort=re.compile(u'公司.*?构成.*?侵权.*?承担.*?责任|综上.*?侵[犯 害].*?权|鉴于.*?应当?承担.*责任|侵犯.*?原告.*?权.*?承担')  # 7
        re_court_said_unfair_competition=[]  # 8
        re_court_said_unfair_competition_w=[]
        re_court_said_unfair_competition_0=re.compile(u'形成.*?竞争关系|符合.*?竞争关系|有?违反?.*?诚实信用原则.*?承担.*?责任|扰乱.*?秩序.*?承担.*?责任|构成.*?不正当竞争.*?承担.*?责任|损害.*?合法利益.*?不正当竞争')
        re_court_said_unfair_competition.append(re_court_said_unfair_competition_0)
        re_court_said_unfair_competition_w.append(1.0)
        re_court_said_unfair_competition_1=re.compile(u'存在竞争关系|有?违反?.*?诚实信用原则')
        re_court_said_unfair_competition.append(re_court_said_unfair_competition_1)
        re_court_said_unfair_competition_w.append(0.7)
        re_court_said_unfair_competition_2=re.compile(u'不正当竞争行为')
        re_court_said_unfair_competition.append(re_court_said_unfair_competition_2)
        re_court_said_unfair_competition_w.append(0.4)
        re_court_said_unfair_competition_3=re.compile(u'《反不正当竞争法》')
        re_court_said_unfair_competition.append(re_court_said_unfair_competition_3)
        re_court_said_unfair_competition_w.append(-0.3)
        self.court_said_unfair_competition=ClaimSet("是否构成不正当竞争",re_court_said_unfair_competition,re_court_said_unfair_competition_w)

        re_court_said_apologize=re.compile(u'赔礼道歉')
        self.court_said_apologize=Claim("是否支持赔礼道歉",re_court_said_apologize)
        re_court_said_image=re.compile(u'承担消除影响|判令.*?消除影响')
        self.court_said_image=Claim("是否支持消除影响",re_court_said_image)
        re_court_said_loss=re.compile(u'本院.*?综合考[虑 量].*?损失|本院综合考虑.*?因素.*支持|对于.*?费.*元|费.*?本院|赔偿.*?经济损失|本院.*?[根 依]据.*?酌情|本院综合考虑.*?酌情')  # 11
        self.court_said_loss=Claim("赔偿数额确定",re_court_said_loss)
        re_court_said_stop_tort=re.compile(u'已.*?删除.*?侵权|撤回.*?侵权|撤回.*?请求')
        self.court_said_stop_tort=Claim("是否已停止侵权",re_court_said_stop_tort)


    def re_claim_match(self):
        self.dividinto_sentence()
        for sentence in self.sentences:
            self.court_said_production.parse_sentence(sentence)
            # 是否享有著作权
            self.court_said_valid.parse_sentence(sentence)
            self.court_said_suit_subject.parse_sentence(sentence)
            # 是否构成直接侵权
            self.court_said_direct_damage.parse_sentence(sentence)
            self.court_said_help_damage.parse_sentence(sentence)
            # 是否符合免责条款
            self.court_said_disclaimer_store.parse_sentence(sentence)
            self.court_said_disclaimer_edit.parse_sentence(sentence)
            self.court_said_disclaimer_check.parse_sentence(sentence)
            self.court_said_disclaimer_attent_duty.parse_sentence(sentence)
            self.court_said_disclaimer_benefit.parse_sentence(sentence)
            self.court_said_disclaimer_delete_content.parse_sentence(sentence)
            # 搜索链接服务是否合法
            self.court_said_link_spread.parse_sentence(sentence)
            self.court_said_link_access.parse_sentence(sentence)
            self.court_said_link_complete.parse_sentence(sentence)
            self.court_said_link_against_will.parse_sentence(sentence)
            self.court_said_link_random.parse_sentence(sentence)
            # 是否构成侵权行为
            self.court_said_tort.parse_sentence(sentence)
            # 是否构成不正当竞争
            self.court_said_unfair_competition.parse_sentence(sentence)

            self.court_said_apologize.parse_sentence(sentence)
            self.court_said_image.parse_sentence(sentence)
            self.court_said_loss.parse_sentence(sentence)
            self.court_said_stop_tort.parse_sentence(sentence)

    def write_claim(self,out):
        prefix_l2="\t"
        prefix_l3="\t\t"
        out.write("%s:\n" % (self.name))
        self.court_said_production.write_paras(out,prefix_l2)
        # 是否享有著作权
        out.write("\t法院认为-是否享有著作权:\n" )
        self.court_said_valid.write_paras(out,prefix_l3)
        self.court_said_suit_subject.write_paras(out,prefix_l3)
        # 是否构成直接侵权
        self.court_said_direct_damage.write_paras(out,prefix_l2)
        # 是否构成帮助侵权
        self.court_said_help_damage.write_paras(out,prefix_l2)
        # 是否符合免责条款
        out.write("\t法院认为-是否符合免责条款:\n" )
        self.court_said_disclaimer_store.write_paras(out,prefix_l3)
        self.court_said_disclaimer_edit.write_paras(out,prefix_l3)
        self.court_said_disclaimer_check.write_paras(out,prefix_l3)
        self.court_said_disclaimer_attent_duty.write_paras(out,prefix_l3)
        self.court_said_disclaimer_benefit.write_paras(out,prefix_l3)
        self.court_said_disclaimer_delete_content.write_paras(out,prefix_l3)
        # 搜索链接服务是否合法
        out.write("\t法院认为-搜索链接服务是否合法:\n" )
        self.court_said_link_spread.write_paras(out,prefix_l3)
        self.court_said_link_access.write_paras(out,prefix_l3)
        self.court_said_link_complete.write_paras(out,prefix_l3)
        self.court_said_link_against_will.write_paras(out,prefix_l3)
        self.court_said_link_random.write_paras(out,prefix_l3)
        # 是否构成侵权行为
        self.court_said_tort.write_paras(out,prefix_l2)
        # 是否构成不正当竞争
        self.court_said_unfair_competition.write_paras(out,prefix_l2)
        self.court_said_apologize.write_paras(out,prefix_l2)
        self.court_said_image.write_paras(out,prefix_l2)
        self.court_said_loss.write_paras(out,prefix_l2)
        self.court_said_stop_tort.write_paras(out,prefix_l2)



class CourtDecision(Party):
    def __init__(self,name,paras):
        super(CourtDecision,self).__init__(name,paras)
        re_court_decision_legal_basis=re.compile(u'依[据 照].*?判决如下|[依 根]据.*?判决如下')
        self.court_decision_legal_basis=Claim("法律依据",re_court_decision_legal_basis)
        re_court_decision_stop_tort=re.compile(u'停止')
        self.court_decision_stop_tort=Claim("停止侵害",re_court_decision_stop_tort)
        re_court_decision_loss=re.compile(u'赔偿.*?经济损失|赔偿.*?合理支出')
        self.court_decision_loss=Claim("赔偿损失",re_court_decision_loss)
        re_court_decision_apologize=re.compile(u'道歉')
        self.court_decision_apologize=Claim("赔礼道歉",re_court_decision_apologize)
        re_court_decision_image=re.compile(u'消除影响')
        self.court_decision_image=Claim("消除影响",re_court_decision_image)
        re_court_decision_reject=re.compile(u'驳回')
        self.court_decision_reject=Claim("驳回诉讼",re_court_decision_reject)
        re_court_decision_cost=re.compile(u'案件受理费.*?负担')
        self.court_decision_cost=Claim("受理费用",re_court_decision_cost)

    def re_claim_match(self):
        self.dividinto_sentence()
        for sentence in self.sentences:
            self.court_decision_legal_basis.parse_sentence(sentence)
            self.court_decision_stop_tort.parse_sentence(sentence)
            self.court_decision_loss.parse_sentence(sentence)
            self.court_decision_apologize.parse_sentence(sentence)
            self.court_decision_image.parse_sentence(sentence)
            self.court_decision_reject.parse_sentence(sentence)
            self.court_decision_cost.parse_sentence(sentence)

    def write_claim(self,out):
        prefix_l2="\t"
        prefix_l3="\t\t"
        out.write("%s:\n" % (self.name))
        self.court_decision_legal_basis.write_paras(out,prefix_l2)
        self.court_decision_stop_tort.write_paras(out,prefix_l2)
        self.court_decision_loss.write_paras(out,prefix_l2)
        self.court_decision_apologize.write_paras(out,prefix_l2)
        self.court_decision_image.write_paras(out,prefix_l2)
        self.court_decision_reject.write_paras(out,prefix_l2)
        self.court_decision_cost.write_paras(out,prefix_l2)



def deal_file(filepath,out,out_l2,out_l3):
    accuser=Side("原告名称")
    defendant=Side("被告名称")
    accuser_claim=Side("原告诉求")
    defendant_argue=Side("被告辩称")
    facts=Side("事实认定")
    court_said=Side("法院认为")
    court_decision=Side("法院判决")

    accuser_flag=False
    defendant_flag=False

    f=codecs.open(filepath, "r", encoding="utf-8")
    pre_op=0
    for line in f:
        line=line.strip()
        #print(line)

        # 判断原告名称
        accusers=re_accuser_name.findall(line)
        if accusers is not None and not accuser_flag:
            for accuser_name in accusers:
                print("原告名称:%s" % (accuser_name))
                accuser.add_para(accuser_name)
                accuser_flag=True

        # 判断被告名称
        defendants=re_defendant_name.findall(line)
        if defendants is not None and not defendant_flag:
            for defendant_name in defendants:
                print("被告名称:%s" % (defendant_name))
                defendant.add_para(defendant_name)
                defendant_flag=True

        op=0  # 默认为0，表示不属于下面这5类
        if re_accuser_claim.findall(line):
            op=1
        if re_defendant_argue.findall(line):
            op=2
        if re_facts.findall(line):
            op=3
        if re_court_said.findall(line):
            op=4
        if re_court_decision.findall(line):
            op=5
        if re_end.findall(line):
            op=6 # 表示end
        #print("op:%d" % (op))
        op_list=[1,2,3,4,5,6]
        if op not in op_list:
            op=pre_op
            # print(op)
        pre_op=op

        for case in switch(op):
            if case(1):
                # print("hello")
                accuser_claim.add_para(line)
                # print(line)
                break
            if case(2):
                defendant_argue.add_para(line)
                # print(line)
                break
            if case(3):
                facts.add_para(line)
                # print(line)
                break
            if case(4):
                court_said.add_para(line)
                # print(line)
                break
            if case(5):
                court_decision.add_para(line)
                # print(line)
                break
            if case(0):
                pass

    f.close()
    accuser.write_paras(out)
    defendant.write_paras(out)
    accuser_claim.write_paras(out)
    defendant_argue.write_paras(out)
    facts.write_paras(out)
    court_said.write_paras(out)
    court_decision.write_paras(out)
    out.close()

    print(len(accuser_claim.paras))
    accuser_claim_l3=AccuserClaim("原告诉求",accuser_claim.paras)
    accuser_claim_l3.re_claim_match()
    accuser_claim_l3.write_claim(out_l3)

    defendant_argue_l3=DefendantArgue("被告辩称",defendant_argue.paras)
    defendant_argue_l3.re_claim_match()
    defendant_argue_l3.write_claim(out_l3)

    facts_l3=Facts("事实认定",facts.paras)
    facts_l3.re_claim_match()
    facts_l3.write_claim(out_l3)

    court_said_l3=CourtSaid("法院认为",court_said.paras)
    court_said_l3.re_claim_match()
    court_said_l3.write_claim(out_l3)

    court_decision_l3=CourtDecision("法院判决",court_decision.paras)
    court_decision_l3.re_claim_match()
    court_decision_l3.write_claim(out_l3)









if __name__=='__main__':
    rootdir=u'cases_new'
    # rootdir=u'影视电视'
    filenames,filepaths=ydir.get_filename_path(rootdir)
    for filename,filepath in zip(filenames,filepaths):
        print(filename)
        print(filepath)
        # dir=os.path.dirname(filepath)  # cases
        cur_dir="./extract_l1_"+rootdir
        cur_dir_l2="./extract_l2_"+rootdir
        cur_dir_l3="./extract_l3_"+rootdir
        ydir.mkdir(cur_dir)
        ydir.mkdir(cur_dir_l2)
        ydir.mkdir(cur_dir_l3)
        outname=cur_dir+"/"+filename
        outname_l2=cur_dir_l2+"/"+filename
        outname_l3=cur_dir_l3+"/"+filename
        print(outname)
        print(outname_l2)
        print(outname_l3)
        out=codecs.open(outname,"w+",encoding="utf-8")
        out_l2=codecs.open(outname_l2,"w+",encoding="utf-8")
        out_l3=codecs.open(outname_l3,"w+",encoding="utf-8")
        deal_file(filepath,out, out_l2, out_l3)







