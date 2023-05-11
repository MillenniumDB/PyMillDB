import sys
import re

s_exp = re.compile(r"^<http://www\.wikidata\.org/entity/(\w\d+)>$")
p_exp = re.compile(r"^<http://www\.wikidata\.org/prop/direct/(\w\d+)>$")
# entity
o1_exp = re.compile(r"^<http://www\.wikidata\.org/entity/(\w\d+)>$")
# string
o2_exp = re.compile(r'^"((?:[^"\\]|\\.)*)"$')
# something with schema
o3_exp = re.compile(r'^"((?:[^"\\]|\\.)*)"\^\^<http://www\.w3\.org/2001/XMLSchema#\w+>$')
# string with idiom
o4_exp = re.compile(r'^"((?:[^"\\]|\\.)*)"@(.+)$')
# other url
o5_exp = re.compile(r"^<(.+)>$")
# point
o6_exp = re.compile(r'^"((?:[^"\\]|\\.)*)"\^\^<http://www\.opengis\.net/ont/geosparql#wktLiteral>$')
# anon
o7_exp = re.compile(r'^_:\w+$')
# math
o8_exp = re.compile(r'^"((?:[^"\\]|\\.)*)"\^\^<http://www\.w3\.org/1998/Math/MathML>$')

anon_count = 0

entities = set()

if __name__ == "__main__":
    input_fname = sys.argv[1]
    output_fname = sys.argv[2]

    input_file = open(input_fname, "r", encoding="utf-8")
    output_file = open(output_fname, "w", encoding="utf-8")

    for line in input_file:
        l = line.split(' ')
        s = l[0]
        p = l[1]
        o = ' '.join(l[2:-1])

        m_s = s_exp.match(s)

        # Subject entity
        entities.add(m_s.groups()[0])

        m_p = p_exp.match(p)

        m_o = o1_exp.match(o)
        if m_o is not None:
            output_file.write(f'{m_s.groups()[0]}->{m_o.groups()[0]} :{m_p.groups()[0]}\n')
            # Object entity
            entities.add(m_o.groups()[0])
            continue

        m_o = o2_exp.match(o)
        if m_o is not None:
            output_file.write(f'{m_s.groups()[0]}->"{m_o.groups()[0]}" :{m_p.groups()[0]}\n')
            continue

        m_o = o3_exp.match(o)
        if m_o is not None:
            output_file.write(f'{m_s.groups()[0]}->"{m_o.groups()[0]}" :{m_p.groups()[0]}\n')
            continue

        m_o = o4_exp.match(o)
        if m_o is not None:
            output_file.write(f'{m_s.groups()[0]}->"{m_o.groups()[0]}" :{m_p.groups()[0]} language:"{m_o.groups()[1]}"\n')
            continue

        m_o = o5_exp.match(o)
        if m_o is not None:
            output_file.write(f'{m_s.groups()[0]}->"{m_o.groups()[0]}" :{m_p.groups()[0]}\n')
            continue

        m_o = o6_exp.match(o)
        if m_o is not None:
            output_file.write(f'{m_s.groups()[0]}->"{m_o.groups()[0]}" :{m_p.groups()[0]}\n')
            continue

        m_o = o7_exp.match(o)
        if m_o is not None:
            anon_count += 1
            output_file.write(f'{m_s.groups()[0]}->_a{anon_count} :{m_p.groups()[0]}\n')
            continue

        m_o = o8_exp.match(o)
        if m_o is not None:
            # TODO: normalize string?
            output_file.write(f'{m_s.groups()[0]}->"{m_o.groups()[0]}" :{m_p.groups()[0]}\n')
            continue

    # Write features for each entity
    for entity in entities:
        output_file.write(f"{entity} feat:[1,1,1]\n")

    input_file.close()
    output_file.close()